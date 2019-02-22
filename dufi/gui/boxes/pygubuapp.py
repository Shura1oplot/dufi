# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import os
import io
import logging
import six

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

import pygubu

# hacks for cx_Freeze
import pygubu.builder.tkstdwidgets
import pygubu.builder.ttkstdwidgets
import pygubu.builder.widgets.dialog
import pygubu.builder.widgets.editabletreeview
import pygubu.builder.widgets.scrollbarhelper
import pygubu.builder.widgets.scrolledframe
import pygubu.builder.widgets.tkscrollbarhelper
import pygubu.builder.widgets.tkscrolledframe
import pygubu.builder.widgets.pathchooserinput

from . import filedialog, messagebox
from .dragndrop import drag_accept_files
from .tkutils import center


if not logging.getLogger("pygubu.builder").handlers:
    logging.getLogger("pygubu.builder").addHandler(logging.StreamHandler())


__all__ = ("GUIApplication", )


class Var(object):

    def __init__(self, builder, hidden=None):
        super(Var, self).__init__()

        self._builder = builder
        self._hidden = hidden

    def __getattr__(self, name):
        if name.startswith("_"):
            return super(Var, self).__getattr__(name)

        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super(Var, self).__setattr__(name, value)
        else:
            self[name] = value

    def __getitem__(self, name):
        if self._hidden:
            try:
                return self._hidden[name]
            except KeyError:
                pass

        return self._builder.get_variable(name).get()

    def __setitem__(self, name, value):
        if self._hidden and name in self._hidden:
            self._hidden[name] = value
        else:
            self._builder.get_variable(name).set(value)


class GUIApplication(object):

    title = None
    icon = None
    modal_window = False
    main_window = "ToplevelMainWindow"

    ui_file = None
    ui_content = None
    resource_dirs = ("data", "resources")
    module_path = None  # must be __file__

    default = {}
    hidden_vars = None

    widgets_not_attach_menu = ()
    entries_extra_menu_items = {}

    # хитрый словарить для затемнения объектов по галочкам
    # {widget_id: (all|any, "var1", "~var2")}
    switches = {}

    def __init__(self, master):
        super(GUIApplication, self).__init__()

        self.master = master
        self.builder = None
        self.mainwindow = None
        self.var = None
        self.callbacks = None
        self.dnd_files = None

        self._dnd = None
        self._taskbar = None
        self.__cb_fix_bind_id = None

    ############################################################################
    # Service methods

    def init(self):  # must be called in the end of __init__() of the child class
        self.builder = pygubu.Builder()
        self.var = Var(self.builder, self.hidden_vars)

        try:
            ui_content = self.get_ui_content()
        except AttributeError:
            ui_content = self.ui_content

        if ui_content:
            self.builder.add_from_string(ui_content)

        else:
            if isinstance(self.ui_file, (tuple, list)):
                ui_path = self.ui_file
            else:
                ui_path = (self.ui_file, )

            self.builder.add_from_file(self.get_resource(*ui_path))

        for res_dir in self.get_resource_dirs():
            self.builder.add_resource_path(res_dir)

        self.mainwindow = self.builder.get_object(self.main_window, self.master)

        # An Expose event is generated whenever all or part of a window should be redrawn
        # (for example, when a window is first mapped or if it becomes unobscured).
        self.__cb_fix_bind_id = \
            self.mainwindow.bind("<Expose>", self.__fix_big_button, "+")

        self.mainwindow.withdraw()

        if self.icon:
            self.mainwindow.iconbitmap(self.get_resource(self.icon))
            # icon = tk.PhotoImage(file=self.get_resource(self.icon))
            # self.master.tk.call("wm", "iconphoto", self.mainwindow, icon)

        self.connect_callbacks()

        for key, default in self.default.items():
            self.var[key] = default

        self.mainwindow.protocol(
            "WM_DELETE_WINDOW", lambda: self.callbacks.on_close_window())

        def _get_ctrl_a_cmd(w):
            if isinstance(w, ttk.Entry):
                return lambda e: self._entry_select_all(w)

            if isinstance(w, tk.Text):
                return lambda e: self._text_select_all(w)

        for obj_id, obj in self.builder.objects.items():
            if obj_id in self.widgets_not_attach_menu:
                continue

            if isinstance(obj.widget, ttk.Entry):
                extra_items = self.entries_extra_menu_items.get(obj_id)
                self.entry_attach_menu(obj.widget, extra_items)
                obj.widget.bind("<Control-a>", _get_ctrl_a_cmd(obj.widget))

            elif isinstance(obj.widget, tk.Text):
                self.text_attach_menu(obj.widget)
                obj.widget.bind("<Control-a>", _get_ctrl_a_cmd(obj.widget))

        if self.title:
            self.mainwindow.title(self.title)

        if self.modal_window:
            self.mainwindow.grab_set()

        self.update_switches()
        center(self.mainwindow, self.master)

    def hide(self):
        self.mainwindow.withdraw()

    def show(self):
        self.mainwindow.update()
        self.mainwindow.deiconify()

        for obj in self.builder.objects.values():
            if isinstance(obj.widget, (ttk.Checkbutton, ttk.Radiobutton)):
                obj.widget.update()

                state = str(obj.widget.cget("state"))

                if state != tk.NORMAL:
                    obj.widget.config(state=tk.NORMAL)
                    obj.widget.event_generate("<Motion>")
                    obj.widget.config(state=state)
                else:
                    obj.widget.event_generate("<Motion>")

                obj.widget.update()

    def get_resource_dirs(self):
        base_paths = []

        module_path = self.module_path

        if module_path:
            if os.path.isfile(module_path):
                module_path = os.path.dirname(module_path)

            base_paths.append(module_path)

        if getattr(sys, "frozen", False):
            base_paths.append(os.path.dirname(sys.executable))
        else:
            base_paths.append(os.path.dirname(sys.argv[0]))

        base_paths.append(os.path.dirname(os.getcwd()))

        resource_dirs = self.resource_dirs

        if isinstance(resource_dirs, str):
            resource_dirs = (resource_dirs, )

        result = []

        for base_path in base_paths:
            for resource_dir in resource_dirs:
                path = os.path.abspath(os.path.join(base_path, resource_dir))

                if os.path.isdir(path):
                    if path not in result:
                        result.append(path)

        return result

    def get_resource(self, *path):
        for res_dir in self.get_resource_dirs():
            file = os.path.join(res_dir, *path)

            if os.path.isfile(file):
                return file

        raise IOError("cannot find resource: {}".format(os.path.join(*path)))

    # def get_ui_content(self):
    #     raise NotImplementedError()

    def on_inited(self):
        pass

    def on_shown(self):
        pass

    def connect_callbacks(self, bag=None):
        if bag is None:
            if self.callbacks is None:
                self.callbacks = self

        else:
            self.callbacks = bag

        self.builder.connect_callbacks(self.callbacks)

    ############################################################################
    # Additional Windows features

    @property
    def taskbar(self):
        if self._taskbar is not None:
            return self._taskbar

        from .taskbar import Taskbar
        self._taskbar = Taskbar(self.mainwindow)
        return self._taskbar

    @property
    def drag_accept_files(self):
        return None

    @drag_accept_files.setter
    def drag_accept_files(self, value):
        if self._dnd is None:
            self._dnd = drag_accept_files(self.mainwindow, self._on_drop_files)

        self._dnd.accept_files = value

    def _on_drop_files(self, files):
        # NOTE: this function will be called from non-main thread
        w = self.master.winfo_containing(*self.master.winfo_pointerxy()) \
            or self.mainwindow
        self.dnd_files = files
        w.event_generate("<<DropFiles>>")

    ############################################################################
    # Standard dialogs

    def showinfo(self, message, title=None):
        return messagebox.showinfo(title or self.title or "Info", message,
                                   parent=self.mainwindow)

    def showwarning(self, message, title=None):
        return messagebox.showwarning(title or self.title or "Warning", message,
                                      parent=self.mainwindow)

    def showerror(self, message, title=None):
        return messagebox.showerror(title or self.title or "Error", message,
                                    parent=self.mainwindow)

    def askyesno(self, message, title=None):
        return messagebox.askyesno(title or self.title, message,
                                   parent=self.mainwindow)

    def fileopenbox(self, *args, **kwargs):
        return filedialog.fileopenbox(*args, parent=self.mainwindow, **kwargs)

    def filesavebox(self, *args, **kwargs):
        return filedialog.filesavebox(*args, parent=self.mainwindow, **kwargs)

    def diropenbox(self, title=None, initialdir=None, mustexist=True):
        return filedialog.diropenbox(title, initialdir, self.mainwindow, mustexist)

    ############################################################################
    # Additional features: checkbutton and radiobutton switches

    def on_checkbutton_switch(self, event=None):
        self.update_switches()

    def update_switches(self):
        for widget_ids, rules in self.switches.items():
            if isinstance(widget_ids, six.string_types):
                widget_ids = (widget_ids, )

            for widget_id in widget_ids:
                if isinstance(rules, six.string_types):
                    opfunc = any
                    varlist = (rules, )
                else:
                    opfunc, varlist = rules[0], rules[1:]

                is_enabled = opfunc(
                    bool(self.var[x.lstrip("~")]) != x.startswith("~")
                    for x in varlist)
                self._set_widget_state(widget_id, is_enabled)

    ############################################################################
    # Entry menu

    def entry_attach_menu(self, w, extra=None):
        menu = tk.Menu(w, tearoff=0)

        if extra:
            def _extra_command(s):
                return lambda: self._entry_set_text(w, s)

            for s in extra:
                menu.add_command(label=s)
                menu.entryconfigure(s, command=_extra_command(s))

            menu.add_separator()

        menu.add_command(label="Cut")
        menu.add_command(label="Copy")
        menu.add_command(label="Paste")
        menu.add_command(label="Delete")
        menu.add_separator()
        menu.add_command(label="Select all")

        menu.entryconfigure(
            "Cut", command=lambda: w.focus_force() or w.event_generate("<<Cut>>"))
        menu.entryconfigure(
            "Copy", command=lambda: w.focus_force() or w.event_generate("<<Copy>>"))
        menu.entryconfigure(
            "Paste", command=lambda: w.focus_force() or w.event_generate("<<Paste>>"))
        menu.entryconfigure(
            "Delete", command=lambda: self._entry_delete(w))
        menu.entryconfigure(
            "Select all", command=lambda: self._entry_select_all(w))

        w.bind("<Button-3><ButtonRelease-3>",
               lambda e: self._entry_show_menu(w, menu, e))

        return menu

    @classmethod
    def _entry_show_menu(cls, w, m, e):
        if not cls._is_widget_state_normal(w):
            return

        state = tk.NORMAL if w.select_present() else tk.DISABLED

        for x in ("Cut", "Copy", "Delete"):
            m.entryconfigure(x, state=state)

        w.focus_force()
        m.tk_popup(e.x_root, e.y_root)

    @classmethod
    def _entry_select_all(cls, w):
        if cls._is_widget_state_normal(w):
            w.select_clear()
            w.selection_range(0, tk.END)
            w.icursor(tk.END)

        return "break"

    @classmethod
    def _entry_delete(cls, w):
        if cls._is_widget_state_normal(w) and w.select_present():
            w.delete(tk.SEL_FIRST, tk.SEL_LAST)

    @classmethod
    def _entry_set_text(cls, w, s):
        if cls._is_widget_state_normal(w):
            w.delete(0, tk.END)
            w.insert(tk.INSERT, s)
            w.icursor(tk.END)

    ############################################################################
    # Text menu

    def text_attach_menu(self, w):
        menu = tk.Menu(w, tearoff=0)

        menu.add_command(label="Save to file...")
        menu.entryconfigure(
            "Save to file...", command=lambda: self._text_save_to_file(w))
        menu.add_separator()

        menu.add_command(label="Cut")
        menu.add_command(label="Copy")
        menu.add_command(label="Paste")
        menu.add_command(label="Delete")
        menu.add_separator()
        menu.add_command(label="Select all")

        menu.entryconfigure(
            "Cut", command=lambda: w.focus_force() or w.event_generate("<<Cut>>"))
        menu.entryconfigure(
            "Copy", command=lambda: w.focus_force() or w.event_generate("<<Copy>>"))
        menu.entryconfigure(
            "Paste", command=lambda: w.focus_force() or w.event_generate("<<Paste>>"))
        menu.entryconfigure(
            "Delete", command=lambda: self._text_delete(w))
        menu.entryconfigure(
            "Select all", command=lambda: self._text_select_all(w))

        w.bind("<Button-3><ButtonRelease-3>",
               lambda e: self._text_show_menu(w, menu, e))

        return menu

    @classmethod
    def _text_show_menu(cls, w, m, e):
        state_selected = tk.NORMAL if w.tag_ranges(tk.SEL) else tk.DISABLED

        if cls._is_widget_state_normal(w):

            for x in ("Cut", "Copy", "Delete"):
                m.entryconfigure(x, state=state_selected)

            m.entryconfigure("Paste", state=tk.NORMAL)

        else:
            m.entryconfigure("Copy", state=state_selected)

            for x in ("Cut", "Paste", "Delete"):
                m.entryconfigure(x, state=tk.DISABLED)

        w.focus_force()
        m.tk_popup(e.x_root, e.y_root)

    @classmethod
    def _text_select_all(cls, w):
        w.tag_add(tk.SEL, 1.0, tk.END)
        w.mark_set(tk.INSERT, tk.END)
        w.see(tk.END)
        return "break"

    @classmethod
    def _text_delete(cls, w):
        if cls._is_widget_state_normal(w) and w.tag_ranges(tk.SEL):
            w.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def _text_save_to_file(self, w):
        fname = self.filesavebox(title="Save text",
                                 filetypes=[("Text files", ".txt"), ],
                                 defaultextension=".txt",
                                 initialfile="unnamed")

        if not fname:
            return

        with io.open(fname, "w", encoding="utf-8") as fp:
            fp.write(w.get(1.0, tk.END))

        self.showinfo("Text saved to: {}".format(os.path.basename(fname)))

    ############################################################################
    # Common callbacks

    def on_button_exit(self, event=None):
        self.close_window()

    def on_button_close(self, event=None):
        self.close_window()

    def on_button_cancel(self, event=None):
        self.close_window()

    def on_close_window(self, event=None):
        self.close_window()

    def close_window(self, event=None):
        if self.modal_window:
            self.mainwindow.destroy()
        else:
            self.master.destroy()

    ############################################################################
    # Various helpers

    def window_fix_max_size(self):
        wh, _ = self.mainwindow.geometry().split("+", 1)
        w, h = wh.split("x")
        self.mainwindow.minsize(int(w), int(h))

    @staticmethod
    def _is_widget_state_normal(w):
        return six.u(str(w.cget("state"))) == six.u(tk.NORMAL)

    def _set_widget_state(self, widget, is_normal):
        if isinstance(widget, six.string_types):
            widget = self.builder.get_object(widget)

        widget.configure(state=tk.NORMAL if is_normal else tk.DISABLED)

        if isinstance(widget, ttk.Combobox):
            # TODO: fix background color for Combobox
            pass

    def _entry_select_text(self, widget_id):
        w = self.builder.get_object(widget_id)
        w.update()
        w.icursor(tk.END)
        w.selection_range(0, tk.END)
        w.xview_moveto(1)
        w.focus_set()

    ############################################################################
    # Private methods

    def __fix_big_button(self, event):
        # http://core.tcl.tk/tk/tktview/4b50b7602849f327892a3be58dfa4442d7a7c07d

        if self.__cb_fix_bind_id is not None:
            self.mainwindow.unbind("<Expose>", self.__cb_fix_bind_id)
            self.__cb_fix_bind_id = None

        self.master.update()
        self.mainwindow.update()

        for obj in self.builder.objects.values():
            if isinstance(obj.widget, (ttk.Checkbutton, ttk.Radiobutton)):
                # http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
                # <Configure> also works (set event.width and event.height)
                obj.widget.event_generate("<Leave>")
