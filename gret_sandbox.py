import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from noise import snoise2


class Root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("gret_sandbox")
        #self.state('zoomed')
        self.geometry("990x640")
        self.main_bg = "gray"
        self.config(bg=self.main_bg)
        self.update()

        # CREATE GLOBALS
        self.CANVAS_SIZE = 600
        self.noise_map = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        self.VALIDATE_FLOAT = (self.register(self.validate_for_float), '%P')
        self.VALIDATE_INT = (self.register(self.validate_for_int), '%P')

        # CREATE GUI
        # additional frames for proper placement purposes
        self.corner_offset = tk.Frame(self, width=10, height=10, bg=self.main_bg)
        self.corner_offset.grid(row=0, column=0, padx=1, pady=1)
        self.col1_width = tk.Frame(self, width=350, height=1, bg=self.main_bg)
        self.col1_width.grid(row=0, column=1, columnspan=7)

        # menu
        base_label = tk.Label(self, bg=self.main_bg, text="Base: ")
        base_label.grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.base_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.base_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w'+'e')
        self.base_entry.insert(0, 0)

        factor_label = tk.Label(self, bg=self.main_bg, text="Factor: ")
        factor_label.grid(row=1, column=3, padx=5, pady=5, sticky='e')
        self.factor_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.factor_entry.grid(row=1, column=4, padx=5, pady=5, sticky='w'+'e')
        self.factor_entry.insert(0, 400)

        octaves_label = tk.Label(self, bg=self.main_bg, text="Octaves: ")
        octaves_label.grid(row=1, column=5, padx=5, pady=5, sticky='e')
        self.octaves_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_INT)
        self.octaves_entry.grid(row=1, column=6, padx=5, pady=5, sticky='w'+'e')
        self.octaves_entry.insert(0, 6)

        persistence_label = tk.Label(self, bg=self.main_bg, text="Persistence: ")
        persistence_label.grid(row=2, column=2, padx=5, pady=5, sticky='e', columnspan=2)
        self.persistence_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.persistence_entry.grid(row=2, column=4, padx=5, pady=5, sticky='w'+'e')
        self.persistence_entry.insert(0, 0.5)

        levels_label = tk.Label(self, bg=self.main_bg, text="Levels: ")
        levels_label.grid(row=2, column=5, padx=5, pady=5, sticky='e')
        self.levels_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_INT)
        self.levels_entry.grid(row=2, column=6, padx=5, pady=5, sticky='w'+'e')
        self.levels_entry.insert(0, 16)

        self.generate_btn = tk.Button(self, text="Generate", command=lambda: self.generate_slow(
            base=float(self.base_entry.get()),
            factor=float(self.factor_entry.get()),
            octaves=int(self.octaves_entry.get()),
            persistence=float(self.persistence_entry.get()),
            levels=int(self.levels_entry.get())
        ))
        self.generate_btn.grid(row=3, column=1, padx=5, pady=5, sticky='w'+'e', columnspan=6)

        # array display area
        bg_array = np.ones((600, 600)) * 50
        self.canvas = tk.Canvas(self, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE)
        self.canvas.grid(row=1, column=10, padx=5, pady=5, rowspan=200)
        self.img = ImageTk.PhotoImage(image=Image.fromarray(bg_array))
        self.map_img = self.canvas.create_image(2, 2, anchor='nw', image=self.img)

    def generate_slow(self, base=0.0, factor=400.0, octaves=6, persistence=0.5, levels=16):
        for x in range(self.CANVAS_SIZE):
            x_factor = x / factor
            for y in range(self.CANVAS_SIZE):
                self.noise_map[x][y] = snoise2(x_factor, y / factor,
                                          octaves=octaves, persistence=persistence,
                                          repeatx=self.CANVAS_SIZE, repeaty=self.CANVAS_SIZE,
                                          base=base)
        # normalize values to 0-levels
        self.noise_map = ((self.noise_map - np.amin(self.noise_map)) / self.noise_map.ptp() * levels).astype(int)
        # rescale to 0-255 (grayscale)
        self.noise_map = self.noise_map / levels * 255
        self.img = ImageTk.PhotoImage(image=Image.fromarray(self.noise_map))
        self.canvas.itemconfig(self.map_img, image=self.img)

    def validate_for_float(self, p):
        if p:
            try:
                float(p)
                return True
            except ValueError:
                return False
        else:
            # Causes ValueError, but allows deleting all chars from entry
            return True

    def validate_for_int(self, p):
        if p:
            try:
                int(p)
                return True
            except ValueError:
                return False
        else:
            # Causes ValueError, but allows deleting all chars from entry
            return True


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

