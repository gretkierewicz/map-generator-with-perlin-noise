from tkinter import Frame, Label, Entry, Scale, VERTICAL


def validate_for_float(p):
    """
    Validation function for better control of entries.
    :param p:
    :return:
    """
    if p:
        try:
            float(p)
            return True
        except ValueError:
            return False
    else:
        # Causes ValueError, but allows deleting all chars from entry
        return True


def validate_for_int(p):
    """
    Validation function for better control of entries.
    :param p:
    :return:
    """
    if p:
        try:
            int(p)
            return True
        except ValueError:
            return False
    else:
        # Causes ValueError, but allows deleting all chars from entry
        return True


class LabeledEntry(Frame):
    """
    LabelEntry - Supporting Frame of simple entries with labels
    Validation for INT and FLOAT included.
    """
    def __init__(self, parent, text="", validate_for='float', value=0.0):
        Frame.__init__(self, parent)

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.VALIDATE_FLOAT = (self.register(validate_for_float), '%P')
        self.VALIDATE_INT = (self.register(validate_for_int), '%P')
        if validate_for == 'int':
            validate_for = self.VALIDATE_INT
        elif validate_for == 'float':
            validate_for = self.VALIDATE_FLOAT
        else:
            # allow no validation at all
            validate_for = None

        label = Label(self, bg=self.main_bg, text=text)
        label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry = Entry(self, width=5, validate='key', validatecommand=validate_for)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.entry.insert(0, value)

    def get(self):
        return self.entry.get()


class LabeledVerticalScale(Frame):
    """
    LabeledVerticalScale - Supporting Frame of vertical slider with labels
    """
    def __init__(self, parent, text="", value=0.0, slider_bind_func=None):
        Frame.__init__(self, parent)

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)
        self.slider_events = ["<ButtonRelease-1>",
                              "<ButtonRelease-3>"]

        self.label = Label(self, text=text)
        self.label.grid(row=0, column=0, padx=5, pady=3, sticky='s')
        self.slider = Scale(self, from_=1, to=0, orient=VERTICAL,
                            resolution=0.01, length=200, width=18)
        self.slider.grid(row=1, column=0, padx=5, pady=5, sticky='n')
        if slider_bind_func is not None:
            for event in self.slider_events:
                self.slider.bind(event, slider_bind_func)
            self.slider.set(value)
        self.label.config(bg=self.slider['bg'])

    def get(self):
        return self.slider.get()
