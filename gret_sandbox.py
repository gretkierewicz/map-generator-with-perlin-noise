import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from noise import snoise2


class GeneratorKit(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, relief='sunken', bd=1)
        self.parent = parent

        self.main_bg = parent.main_bg
        self.config(bg=self.main_bg)

        self.CANVAS_SIZE = 600
        self.noise_array = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        self.VALIDATE_FLOAT = (self.register(self.validate_for_float), '%P')
        self.VALIDATE_INT = (self.register(self.validate_for_int), '%P')

        # CREATE GUI
        # menu
        base_label = tk.Label(self, bg=self.main_bg, text="Base: ")
        base_label.grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.base_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.base_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w'+'e')
        self.base_entry.insert(0, 0)

        scale_label = tk.Label(self, bg=self.main_bg, text="Scale: ")
        scale_label.grid(row=1, column=3, padx=5, pady=5, sticky='e')
        self.scale_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.scale_entry.grid(row=1, column=4, padx=5, pady=5, sticky='w'+'e')
        self.scale_entry.insert(0, 400)

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

        factor_label = tk.Label(self, bg=self.main_bg, text="Factor: ")
        factor_label.grid(row=2, column=5, padx=5, pady=5, sticky='e')
        self.factor_entry = tk.Entry(self, width=5, validate='key', validatecommand=self.VALIDATE_FLOAT)
        self.factor_entry.grid(row=2, column=6, padx=5, pady=5, sticky='w' + 'e')
        self.factor_entry.insert(0, 16)

        self.generate_btn = tk.Button(self, text="Generate", command=lambda: self.generate_slow(
            base=float(self.base_entry.get()),
            scale=float(self.scale_entry.get()),
            octaves=int(self.octaves_entry.get()),
            persistence=float(self.persistence_entry.get())
        ))
        self.generate_btn.grid(row=3, column=1, padx=5, pady=5, sticky='w'+'e', columnspan=2)

        self.show_btn = tk.Button(self, text="Show", command=self.visualize_data)
        self.show_btn.grid(row=3, column=3, padx=5, pady=5, sticky='w'+'e', columnspan=2)

        self.destroy_btn = tk.Button(self, text="Delete", command=self.self_destroy)
        self.destroy_btn.grid(row=3, column=5, padx=5, pady=5, sticky='w'+'e', columnspan=2)

    def generate_slow(self, base=0.0, scale=400.0, octaves=6, persistence=0.5):
        for x in range(self.CANVAS_SIZE):
            x_scale = x / scale
            for y in range(self.CANVAS_SIZE):
                self.noise_array[x][y] = snoise2(x_scale, y / scale,
                                                 octaves=octaves, persistence=persistence,
                                                 repeatx=self.CANVAS_SIZE, repeaty=self.CANVAS_SIZE,
                                                 base=base)

    def visualize_data(self):
        noise_map = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        # normalize values to 0-levels
        if self.noise_array.ptp():
            noise_map = ((self.noise_array - np.amin(self.noise_array))
                         / self.noise_array.ptp() * self.parent.levels).astype(int)
        else:
            noise_map[:, :] = self.noise_array[:, :]
        # rescale to 0-255 (grayscale)
        noise_map = noise_map / self.parent.levels * 255
        self.parent.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
        self.parent.canvas.itemconfig(self.parent.map_img, image=self.parent.img)

    def self_destroy(self):
        self.parent.dynamic_frames.remove(self)
        self.destroy()
        self.parent.group_generation_kits()

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


class Root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("gret_sandbox")
        #self.state('zoomed')
        self.geometry("1200x640")
        self.main_bg = "gray"
        self.config(bg=self.main_bg)
        self.update()

        self.dynamic_frames = []
        self.CANVAS_SIZE = 600
        self.levels = 16

        # additional frames for proper placement purposes
        self.corner_offset = tk.Frame(self, width=10, height=10, bg=self.main_bg)
        self.corner_offset.grid(row=0, column=0, padx=1, pady=1)

        # column 1 - place for gradient and river generators

        # column 2 - generator kits
        self.col1_width = tk.Frame(self, width=300, height=5, bg=self.main_bg)
        self.col1_width.grid(row=0, column=2, columnspan=3, sticky='n')
        # generator kits
        generator_kit = GeneratorKit(self)
        self.dynamic_frames.append(generator_kit)
        generator_kit.grid(row=1, column=2, pady=3, sticky='n')
        # button for adding layers (generator kits)
        self.make_frame_btn = tk.Button(self, text="Add layer", command=self.new_generator_kit)
        self.make_frame_btn.grid(row=2, column=2, padx=3, pady=3, sticky='we')

        # column 3 - array display area
        bg_array = np.ones((600, 600))
        self.canvas = tk.Canvas(self, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE)
        # silly rowspan=500 - not to disturb placement of dynamic generator kits as it get's messy with low numbers
        self.canvas.grid(row=1, column=10, padx=5, pady=5, rowspan=500, sticky='n')
        self.img = ImageTk.PhotoImage(image=Image.fromarray(bg_array))
        self.map_img = self.canvas.create_image(2, 2, anchor='nw', image=self.img)

    def new_generator_kit(self):
        if len(self.dynamic_frames) < 5:
            generator_kit = GeneratorKit(self)
            self.dynamic_frames.append(generator_kit)
            self.group_generation_kits()

    def group_generation_kits(self):
        for i in range(len(self.dynamic_frames)):
            self.dynamic_frames[i].grid(row=i+2, column=2, pady=3, sticky='n')
        self.make_frame_btn.grid(row=len(self.dynamic_frames)+2)
        if len(self.dynamic_frames) > 4:
            self.make_frame_btn.grid_remove()

    def make_map(self):
        pass


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

