# [SublimeLinter @python:3]

from pygubu.widgets.simpletooltip import ToolTip


def attach_tooltip(widget, text_or_func):
    toolTip = ToolTip(widget)

    if callable(text_or_func):
        func = text_or_func

        def on_enter(event):
            text = func()

            if text is not None:
                toolTip.showtip(str(text))

    else:
        text = str(text_or_func)

        def on_enter(event):
            toolTip.showtip(text)

    def on_leave(event):
        toolTip.hidetip()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


class attach_tooltip_delay(object):

    def __init__(self, master, widget, text_or_func, delay=500):
        super(attach_tooltip_delay, self).__init__()

        self.master = master
        self.delay = delay

        if callable(text_or_func):
            func = text_or_func
            self.callback = func
        else:
            text = str(text_or_func)
            self.callback = lambda: text

        self.last_id = None
        self.tooltip = ToolTip(widget)
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        if self.last_id is not None:
            self.master.after_cancel(self.last_id)

        self.last_id = self.master.after(self.delay, self.show_tip)

    def on_leave(self, event):
        if self.last_id is None:
            self.tooltip.hidetip()
        else:
            self.master.after_cancel(self.last_id)
            self.last_id = None

    def show_tip(self):
        text = self.callback()

        if text is not None:
            self.tooltip.showtip(str(text))

        self.last_id = None
