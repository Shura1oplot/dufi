#!/usr/bin/env python3
# [SublimeLinter @python:3]

import sys
import os
import time
from collections import namedtuple
import ctypes
import json
import re

import threading
from queue import Queue
import subprocess as sp

import traceback
import locale

import tkinter as tk
from tkinter import ttk

from . import boxes
from .boxes.tktooltip import attach_tooltip_delay
from .boxes.exceptioncatcher import TkExceptionCatcher

from .balloontip import balloon_tip

from .. import dufi_commands, InvalidCommandArgs, __version__


class CommandExecution(object):

    system_encoding = locale.getpreferredencoding() or "utf-8"

    def __init__(self, view):
        super(CommandExecution, self).__init__()

        self.view = view

        self.proc = None
        self.timestamp = None
        self.output = None
        self.cancelled = None
        self.files_total = None
        self.files_done = None

    def is_running(self):
        return self.proc and self.proc.poll() is None

    def run(self):
        if self.is_running():
            self.view.showerror("Command is already running!")
            return

        self.output = Queue()
        self.cancelled = False
        self.files_total = None
        self.files_done = None

        self.timestamp = time.time()
        self.proc = sp.Popen(self._get_cmd(), bufsize=1, stdin=sp.PIPE,
                             stdout=sp.PIPE, stderr=sp.STDOUT)

        for file in self.view.var.files:
            self.proc.stdin.write((file + "\n").encode(self.system_encoding))

        self.proc.stdin.close()

        threading.Thread(target=self._read_output).start()

        self.view.set_execution_running()
        self.view.set_progress(0, 0)
        self.view.add_output_lines(
            ["Executing {}...".format(self.view.selected_command_name)])
        self.view.master.after(0, self._consume_output)

    def _get_cmd(self):
        command = dufi_commands[self.view.selected_command]
        return command.get_cmd_args(self.view)

    def _read_output(self):
        for line in self.proc.stdout:
            self.output.put(line)

        self.proc.wait()
        self.output.put(None)

    def _consume_output(self):
        output_lines = []
        finished = False
        progress_current = None
        execution_status = None

        while not self.output.empty():
            line = self.output.get()

            if line is None:
                finished = True
                break

            line = line.rstrip().decode(self.system_encoding)

            m = re.match(r"^Progress: (\d+)%$", line)

            if m:
                progress_current = int(m.group(1))
                continue

            m = re.match(r"^Processing (\d+)/(\d+): .+$", line)

            if m:
                execution_status = line
                self.files_done = int(m.group(1)) - 1
                self.files_total = int(m.group(2))
                progress_current = 0

            output_lines.append(line)

        if finished and self.cancelled:
            output_lines.append("Command interrupted.")

        if execution_status is not None:
            self.view.var.execution_status = execution_status

        self.view.add_output_lines(output_lines)

        if progress_current is not None:
            progress_overall = (self.files_done * 100 + progress_current) \
                // self.files_total

            self.view.set_progress(progress_overall, progress_current)

        et = time.time() - self.timestamp
        self.view.var.execution_time = "{:d}h {:d}m {:d}s".format(
            int(et / 60 / 60), int((et / 60) % 60), int(et % 60))

        if not finished:
            self.view.master.after(100, self._consume_output)
            return

        if self.cancelled:
            self.view.set_execution_canceled()
        elif self.proc.returncode != 0:
            self.view.set_execution_error()
        else:
            self.view.set_progress(100, 100)
            self.view.var.execution_status = "Finished."
            self.view.set_execution_finished()

    def interrupt(self):
        if not self.is_running():
            return None

        if not self.view.askyesno("Interrupt command execution?"):
            return False

        self.cancelled = True
        self.proc.terminate()
        return True


class Application(boxes.GUIApplication):

    title = "DuFi Tools v{}".format(__version__)
    icon = "dufi-gui-win.ico"

    ui_file = "dufi-gui.ui"
    resource_dirs = os.path.join(os.path.dirname(__file__), "resources")

    default = dufi_commands.get_default()
    switches = dufi_commands.get_switches()

    pages = ("Settings", "Execution")

    commands = dufi_commands.get_names()

    def __init__(self, master):
        super(Application, self).__init__(master)

        self.hidden_vars = {"files": []}
        self.cmd = CommandExecution(self)

        self.init()

        self.drag_accept_files = True

        bgo = self.builder.get_object
        self._page_manager = bgo("NotebookPageManager")
        self._commands_manager = bgo("NotebookCommandsManager")
        self._listbox_commands = bgo("ListboxCommands")
        self._output = bgo("TextOutput")
        self._output_scroll = bgo("ScrollbarsOutput")
        self._cc_tv = bgo("editabletreeviewOtherParameters")
        self._cct_col_value = "ColumnOtherParameterValue"

        for cmd in dufi_commands:
            cmd.init_gui(self)

        def resize_tk_messages(e):
            for cmd in dufi_commands:
                if cmd.gui_info_message_widget:
                    widget = self.builder.get_object(cmd.gui_info_message_widget)
                    widget.configure(width=max(e.width - 20, 400))

        bgo("NotebookCommandsManager").bind("<Configure>", resize_tk_messages)
        resize_tk_messages(namedtuple("_", ("width", ))(
            bgo("NotebookCommandsManager").winfo_width()))

        cb = ttk.Combobox()
        cb.unbind_class("TCombobox", "<MouseWheel>")
        cb.unbind_class("TCombobox", "<Button-4>")
        cb.unbind_class("TCombobox", "<ButtonPress-4>")
        cb.unbind_class("TCombobox", "<Button-5>")
        cb.unbind_class("TCombobox", "<ButtonPress-5>")

        for command in self.commands:
            self._listbox_commands.insert(tk.END, " " + command)

        self.select_command(0)

        self.show()

        self._listbox_commands.focus_set()

    # navigation - pages

    def activate_page_view(self, page):
        pm = self._page_manager
        pm.select(pm.tabs()[self.pages.index(page)])
        self.drag_accept_files = page == "Settings"
        self.taskbar.set_progress_state("no_progress")

    # navigation - commands

    @property
    def selected_command(self):
        sel = self._listbox_commands.curselection()

        if not sel:
            return None

        return self.commands[int(sel[0])]

    @property
    def selected_command_name(self):
        return dufi_commands[self.selected_command].get_name(self)

    def select_command(self, command):
        if isinstance(command, str):
            command = self.commands.index(command)

        lb = self._listbox_commands
        lb.selection_clear(0, tk.END)
        lb.selection_set(command)
        lb.activate(command)
        lb.see(command)

    def activate_command_view(self, command):
        if isinstance(command, str):
            command = self.commands.index(command)

        self.var.command_help \
            = dufi_commands[self.commands[command]].gui_description

        cm = self._commands_manager
        cm.select(cm.tabs()[command])
        self.update_switches()

    def on_command_selected(self, event=None):
        sel = self._listbox_commands.curselection()

        if sel:
            self.activate_command_view(int(sel[0]))
        else:
            self.select_command(0)
            self.activate_command_view(0)

    def on_listbox_commands_key_up(self, event=None):
        sel = self._listbox_commands.curselection()

        command = int(sel[0]) - 1 if sel else 0

        if command >= 0:
            self.select_command(command)
            self.activate_command_view(command)

    def on_listbox_commands_key_down(self, event=None):
        sel = self._listbox_commands.curselection()

        command = int(sel[0]) + 1 if sel else 0

        if command < len(self.commands):
            self.select_command(command)
            self.activate_command_view(command)

    # execution views

    def set_execution_running(self):
        self.var.executing_caption = \
            "{}: Executing...".format(self.selected_command_name)
        self.var.executing_description \
            = "Please wait while the application performs its tasks."
        self.builder.get_object("ButtonSetup").config(state=tk.DISABLED)
        self.builder.get_object("ButtonRestart").config(state=tk.DISABLED)
        self.var.button_cancel_text = "Cancel"
        self.taskbar.set_progress_state("normal")

    def set_execution_finished(self):
        self.var.executing_caption = \
            "{}: Finished".format(self.selected_command_name)
        self.var.executing_description \
            = "All done! You may now close the program or run one more command."
        self._set_buttons_ready()
        self.taskbar.set_progress_state("no_progress")

        if self.mainwindow.state() != tk.NORMAL:
            balloon_tip("DuFi Tools", "Task is completed",
                        icon_type="info", block=False)

    def set_execution_canceled(self):
        self.var.executing_caption = \
            "{}: Canceled".format(self.selected_command_name)
        self.var.executing_description \
            = ("Execution of the command has been interrupted. "
               "You may setup and run it again.")
        self._set_buttons_ready()
        self.taskbar.set_progress_state("error")

    def set_execution_error(self):
        self.var.executing_caption = \
            "{}: Error!".format(self.selected_command_name)
        self.var.executing_description \
            = "The command has been stopped because of an error."
        self._set_buttons_ready()
        self.taskbar.set_progress_state("error")

        if self.mainwindow.state() != tk.NORMAL:
            balloon_tip("DuFi Tools", "Something went wrong...",
                        icon_type="error", block=False)

    def _set_buttons_ready(self):
        self.builder.get_object("ButtonSetup").config(state=tk.NORMAL)
        self.builder.get_object("ButtonRestart").config(state=tk.NORMAL)
        self.var.button_cancel_text = "Close"

    # execution output, status and progress

    def add_output_lines(self, lines):

        _, vsb_pos = self._output_scroll.vsb.get()
        text_empty = self._output.get(1.0, tk.END) == "\n"

        row, col = map(int, self._output.index("end -1 chars").split("."))

        lines = [line.rstrip() for line in lines]

        while lines and not lines[-1]:
            lines = lines[:-1]

        if not lines:
            return

        self._set_widget_state(self._output, is_normal=True)

        if col > 0:
            self._output.insert(tk.END, "\n")

        for i, line in enumerate(lines, 1):
            self._output.insert(tk.END, line)

            if i < len(lines):
                self._output.insert(tk.END, "\n")

        self._set_widget_state(self._output, is_normal=False)

        if vsb_pos == 1.0 or text_empty:
            self._output.update()
            self._output.see(tk.END)

    def set_progress(self, overall, current):
        self.var.progress_current = current
        self.var.progress_overall = overall
        self.taskbar.set_progress_value(overall)

    # files

    def on_drop_files(self, event=None):
        if len(self.dnd_files) == 1:
            _, ext = os.path.splitext(self.dnd_files[0])

            if ext.lower() == ".dufisettings":
                self._load_settings(self.dnd_files[0])
                self._update_files_info()
                return

        for file in self.dnd_files:
            if file not in self.var.files:
                self.var.files.append(file)

        self._update_files_info()

    def _load_settings(self, file):
        settings = json.load(open(file, encoding="utf-8"))

        for key, value in settings.items():
            if key == "active_command":
                self.select_command(value)
                self.activate_command_view(value)

            else:
                self.var[key] = value

    def on_button_add_files(self, event=None):
        files = self.fileopenbox(title="DuFi :: Select CSV Files", multiple=True)

        if not files:
            return

        for file in files:
            if file not in self.var.files:
                self.var.files.append(file)

        self._update_files_info()

    def on_button_clear_files(self, event=None):
        self.var.files = []
        self._update_files_info()

    def _update_files_info(self):
        if not self.var.files:
            self.var.files_info = "No files selected"
        else:
            self.var.files_info = "{} file{} selected (?)".format(
                len(self.var.files), "" if len(self.var.files) == 1 else "s")

    # buttons

    def on_button_start(self, event=None):
        error = self.validate()

        if error:
            self.showerror(error)
            return

        self.activate_page_view("Execution")
        self.cmd.run()

    def on_button_setup(self, event=None):
        self.activate_page_view("Settings")

    def on_button_restart(self, event=None):
        self.cmd.run()

    def on_button_close(self, event=None):
        self.close_window()

    def on_button_cancel(self, event=None):
        if self.cmd.interrupt() is None:
            self.close_window()

    def on_close_window(self, event=None):
        interrupted = self.cmd.interrupt()

        if interrupted is None or interrupted:
            self.close_window()

    def on_button_save_settings(self, event=None):
        command_name = self.selected_command
        command = dufi_commands[command_name]

        if command.gui_variables is None:
            self.showerror("Cannot save settings for this command!")
            return

        settings = {"active_command": command_name}

        if self.var.files:
            settings["files"] = self.var.files

        for var_name in command.gui_variables:
            settings[var_name] = self.var[var_name]

        file = self.filesavebox(
            title="DuFi :: Save Settings",
            filetypes=(("DuFi Settings (*.dufisettings)", "*.dufisettings"), ),
            defaultextension=".dufisettings")

        if not file:
            return

        json.dump(settings, open(file, "w", encoding="utf-8"), indent=4)
        self.showinfo("Settings have been saved.")

    def on_button_convert_output_browse_dir(self, event=None):
        directory = self.diropenbox(title="DuFi :: Select Directory")

        if not directory:
            return

        directory = directory.replace("/", "\\")
        self.var.convert_output = os.path.join(directory, "!.!")

    def on_button_convert_output_browse_file(self, event=None):
        file = self.fileopenbox(title="DuFi :: Select File")

        if not file:
            return

        self.var.convert_output = file.replace("/", "\\")

    def on_button_excel_output_browse(self, event=None):
        directory = self.diropenbox(
            title="DuFi :: Select Directory")

        if not directory:
            return

        directory = directory.replace("/", "\\")
        self.var.excel_output = os.path.join(directory, "!.csv")

    def on_button_working_time_holidays(self, event=None):
        file = os.path.join(self._get_exe_dir(), "holidays.txt")

        if not os.path.exists(file):
            try:
                open(file, "w").close()
            except IOError:
                self.showerror("Cannot create holidays.txt")
                return

        os.startfile(file)

    def on_button_working_time_half_holidays(self, event=None):
        file = os.path.join(self._get_exe_dir(), "half-holidays.txt")

        if not os.path.exists(file):
            try:
                open(file, "w").close()
            except IOError:
                self.showerror("Cannot create half-holidays.txt")
                return

        os.startfile(file)

    # validators

    def validate(self):
        command = self.selected_command

        if not command:
            return "No command selected! How did this happen?"

        try:
            dufi_commands[command].validate_cmd_args(self)
        except InvalidCommandArgs as e:
            return e.error_text.capitalize()

    def entry_number_validate(self, value):
        if not value:
            return True

        try:
            assert int(value) >= 0
        except (ValueError, AssertionError):
            return False
        else:
            return True

    def entry_separator_validate(self, value):
        return not value \
            or (len(value) > 2 and value.startswith("  ") and value[2] != " ") \
            or value == "<TAB>"

    def entry_separator_invalid(self, action, new_value, old_value):
        if not new_value.strip():
            self.var.separator = ""
            return

        # Type of action (1=insert, 0=delete, -1 for others)
        if action == "1" and len(new_value) - len(old_value) == 1:
            i, x = self._get_char_inserted(old_value, new_value)

            if i is not None and i <= 1:
                spaces = " " * (len(old_value) - len(old_value.lstrip()))
                self.var.separator = spaces + x + old_value.lstrip()
                self._separator_set_icursor(3)
                return

        if action == "0" and len(old_value) - len(new_value) == 1 \
                and len(old_value.lstrip()) - len(new_value.lstrip()) == 0:
            spaces = " " * (len(old_value) - len(old_value.lstrip()))
            value = spaces + old_value.lstrip()[1:]

            if not value.strip():
                self.var.separator = ""
                return

            self.var.separator = value
            self._separator_set_icursor(2)
            return

        self.var.separator = "  {}".format(new_value.lstrip())
        self._separator_set_icursor(tk.END)

    @staticmethod
    def _get_char_inserted(old, new):
        for i, (a, b) in enumerate(zip(old, new)):
            if a != b:
                return i, b

        return None, None

    def _separator_set_icursor(self, pos):
        w = self.master.focus_get()

        if isinstance(w, ttk.Combobox):
            w.icursor(pos)

    # tooltip helpers

    def attach_tooltip(self, obj_id, text):
        attach_tooltip_delay(self.master, self.builder.get_object(obj_id), text)

    def attach_files_info_tooltip(self, object_id):
        widget = self.builder.get_object(object_id)

        def callback():
            if not self.var.files:
                return

            lines = []

            for i, file in enumerate(self.var.files):
                if i == 10:
                    break

                fname = os.path.basename(file)

                if len(fname) > 50:
                    fname = "{}..{}".format(fname[:24], fname[-24:])

                lines.append(fname)

            tail = len(self.var.files) - len(lines)

            if tail > 0:
                lines.append("... and {} more.".format(tail))

            return "\n".join(lines)

        attach_tooltip_delay(self.master, widget, callback)

    # other command tree

    def get_other_command_args(self):
        args = []

        for item in self._cc_tv.get_children():
            args.append(self._cc_tv.item(item, "values"))

        return args

    def _update_other_command_help(self, text):
        w = self.builder.get_object("TextOtherParameterDescription")
        w.configure(state=tk.NORMAL)
        w.delete(1.0, tk.END)
        w.insert(1.0, text.rstrip())
        w.update()
        w.see(tk.END)
        w.configure(state=tk.DISABLED)

    def on_other_command_selected(self, event=None):
        dufcmd = dufi_commands.get_by_name_cli(self.var.other_command)

        for item in self._cc_tv.get_children():
            self._cc_tv.delete(item)

        for arg_name, spec, _ in dufcmd.get_command_schema():
            if arg_name in ("--list", "files"):
                continue

            if spec.get("action") == "truefalse":
                value = "No"
            else:
                default = spec.get("default", "")
                value = str(default) if default is not None else ""

            self._cc_tv.insert("", tk.END, values=(arg_name, value))

        self._cc_tv.selection_set("")

        self._update_other_command_help("{} - {}".format(
            dufcmd.cli_command, dufcmd.cli_command_help))

    def on_other_command_param_value_edit(self, event=None):
        col, item = self._cc_tv.get_event_info()

        if col != self._cct_col_value:
            return

        param_name = self._cc_tv.item(item)["values"][0]
        dufcmd = dufi_commands.get_by_name_cli(self.var.other_command)

        self._cc_tv.inplace_combobox(self._cct_col_value, item, (), readonly=False)
        cb = self._cc_tv._inplace_widgets[self._cct_col_value]
        cb.unbind("<<ComboboxSelected>>")

        schema = {name: (spec, help) for name, spec, help
                  in dufcmd.get_command_schema()}

        spec, help = schema[param_name]
        action = spec.get("action")

        if action == "truefalse":
            cb["values"] = ("Yes", "No")
            cb.configure(state="readonly")

        elif action in ("browse_file", "browse_dir"):
            cb["values"] = ("Browse...", )
            cb.configure(state=tk.NORMAL)

            if action == "browse_file":
                box_type = spec.get("box_type", "open")

                if box_type == "open":
                    open_action = self.fileopenbox
                elif box_type == "save":
                    open_action = self.filesavebox
                else:
                    raise ValueError(box_type)

                open_action_kwargs = {"title": "DuFi :: Select File"}
                open_action_kwargs.update(spec.get("box_args", {}))

            else:  # browse_dir
                open_action = self.diropenbox
                open_action_kwargs = {"title": "DuFi :: Select Directory"}
                open_action_kwargs.update(spec.get("box_args", {}))

            def callback(event=None):
                if cb.get() != "Browse...":
                    return

                path = open_action(**open_action_kwargs)

                cb.set("")
                cb.set(path or "")
                cb.update()
                cb.select_range(0, tk.END)
                cb.icursor(tk.END)
                cb.xview_moveto(1)

            cb.bind("<<ComboboxSelected>>", callback)

        elif spec.get("choices"):
            choices = list(spec["choices"])

            if spec.get("default"):
                default = spec.get("default")
                choices = [default, ] + [x for x in choices if x != default]

            cb["values"] = [str(x) for x in choices]
            cb.configure(state="readonly")

        elif spec.get("default"):
            cb["values"] = (str(spec["default"]), )
            cb.configure(state=tk.NORMAL)

        else:
            cb["values"] = ()
            cb.configure(state=tk.NORMAL)

        self._update_other_command_help("{} {} - {}".format(
            dufcmd.cli_command, param_name,
            help or "<help text not available>"))

    # other functions

    @staticmethod
    def _get_exe_dir():
        if getattr(sys, "frozen", False):
            prog_path = sys.executable
        else:
            prog_path = sys.argv[0]

        return os.path.dirname(os.path.abspath(prog_path))


def main(argv=sys.argv):
    if not getattr(sys, "frozen", False):
        ctypes.windll.user32.SetProcessDPIAware()

    if len(argv) > 1:
        from ..cli import main as main_

        try:
            return main_(argv)
        except SystemExit as e:
            return e.code
        except:
            if sys.stderr is None or sys.stderr.closed:
                raise

            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
            return 1

    boxes.utils.set_system_encoding()
    boxes.utils.set_dpi_aware()

    tk.CallWrapper = TkExceptionCatcher
    TkExceptionCatcher.root = root = tk.Tk()
    root.withdraw()

    boxes.ttkstyles.create_ttk_styles()
    ttk.Style().configure("Treeview", rowheight=24)  # FIXME

    Application(root)
    root.mainloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
