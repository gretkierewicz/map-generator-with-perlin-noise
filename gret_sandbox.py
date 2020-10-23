import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from noise import snoise2


def validate_for_float(p):
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
    if p:
        try:
            int(p)
            return True
        except ValueError:
            return False
    else:
        # Causes ValueError, but allows deleting all chars from entry
        return True


class ControlElement(tk.Frame):
    def __init__(self, parent, text="", validatefor='float', value=0.0):
        tk.Frame.__init__(self, parent)

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.VALIDATE_FLOAT = (self.register(validate_for_float), '%P')
        self.VALIDATE_INT = (self.register(validate_for_int), '%P')
        validatefor = self.VALIDATE_INT if validatefor == 'int' else self.VALIDATE_FLOAT

        label = tk.Label(self, bg=self.main_bg, text=text)
        label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry = tk.Entry(self, width=5, validate='key', validatecommand=validatefor)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.entry.insert(0, value)

    def get(self):
        return self.entry.get()


class GeneratorKit(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, relief='sunken', bd=1)
        self.root = parent.master

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.CANVAS_SIZE = 600
        self.noise_array = None

        # CREATE GUI - menu
        # base = seed for generator
        self.base_entry = ControlElement(self, text="Base: ", validatefor='int', value=0)
        self.base_entry.grid(row=0, column=0, sticky='e')
        # scale = how much to zoom in
        self.scale_entry = ControlElement(self, text="Scale: ", validatefor='int', value=400)
        self.scale_entry.grid(row=0, column=1, sticky='e')
        # octaves = number of layers of detail
        self.octaves_entry = ControlElement(self, text="Octaves: ", validatefor='int', value=6)
        self.octaves_entry.grid(row=0, column=2, sticky='e')
        # persistence = factor of contribution of higher octaves
        self.persistence_entry = ControlElement(self, text="Persistence: ", validatefor='float', value=0.5)
        self.persistence_entry.grid(row=1, column=0, columnspan=2, sticky='e')
        # factor = contribution of this array in the whole map
        self.factor_entry = ControlElement(self, text="Factor: ", validatefor='float', value=1)
        self.factor_entry.grid(row=1, column=2, sticky='e')

        self.generate_btn = tk.Button(self, text="Generate", command=lambda: self.generate_slow(
            base=float(self.base_entry.get()),
            scale=float(self.scale_entry.get()),
            octaves=int(self.octaves_entry.get()),
            persistence=float(self.persistence_entry.get())
        ))
        self.generate_btn.grid(row=2, column=0, padx=5, pady=5, sticky='we')

        self.show_btn = tk.Button(self, text="Show", command=self.visualize_data)
        self.show_btn.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        self.show_btn.grid_remove()

        self.destroy_btn = tk.Button(self, text="Delete", command=self.self_destroy, bg='darkred', fg='lightgray')
        self.destroy_btn.grid(row=2, column=2, padx=5, pady=5, sticky='we')

    def generate_slow(self, base=0.0, scale=400.0, octaves=6, persistence=0.5):
        self.noise_array = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        for x in range(self.CANVAS_SIZE):
            x_scale = x / scale
            for y in range(self.CANVAS_SIZE):
                self.noise_array[x][y] = snoise2(x_scale, y / scale,
                                                 octaves=octaves, persistence=persistence,
                                                 repeatx=self.CANVAS_SIZE, repeaty=self.CANVAS_SIZE,
                                                 base=base)
        if self.root.img is None:
            self.visualize_data()
        self.show_btn.grid()

    def visualize_data(self):
        if self.noise_array is not None:
            noise_map = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
            # normalize values to 0-levels
            if self.noise_array.ptp():
                noise_map = ((self.noise_array - np.amin(self.noise_array))
                             / self.noise_array.ptp() * self.root.levels).astype(int)
            else:
                noise_map[:, :] = self.noise_array[:, :]
            # rescale to 0-255 (grayscale)
            noise_map = noise_map / self.root.levels * 255
            self.root.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
            self.root.canvas.itemconfig(self.root.map_img, image=self.root.img)

    def self_destroy(self):
        self.root.dynamic_frames.remove(self)
        self.destroy()
        self.root.group_generation_kits()


class Root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.title("gret_sandbox")
        #self.state('zoomed')
        self.geometry("1240x640")
        self.main_bg = "gray"
        self.config(bg=self.main_bg)
        self.update()

        self.dynamic_frames = []
        self.CANVAS_SIZE = 600
        self.levels = 16

        # additional frames for proper placement purposes
        self.corner_offset = tk.Frame(self, width=10, height=10, bg=self.main_bg)
        self.corner_offset.grid(row=0, column=0)

        # column 1 - place for gradient and river generators
        self.col1_frame = tk.Frame(self, bg=self.main_bg)
        self.col1_frame.grid(row=1, column=1, sticky='n')
        self.col1_width = tk.Frame(self.col1_frame, width=300, bg=self.main_bg)
        self.col1_width.grid(row=0, column=0)
        # displaying the whole map button
        self.make_frame_btn = tk.Button(self.col1_frame, text="Display whole map", command=self.display_map)
        self.make_frame_btn.grid(row=1, column=0, padx=3, pady=3, sticky='we')

        # column 2 - generator kits
        self.col2_frame = tk.Frame(self, bg=self.main_bg)
        self.col2_frame.grid(row=1, column=2, sticky='n')
        self.col2_width = tk.Frame(self.col2_frame, width=300, bg=self.main_bg)
        self.col2_width.grid(row=0, column=0)
        # create basic generator kit
        generator_kit = GeneratorKit(self.col2_frame)
        self.dynamic_frames.append(generator_kit)
        generator_kit.grid(row=1, column=0, pady=3, sticky='n')
        # button for adding layers (generator kits)
        self.make_frame_btn = tk.Button(self.col2_frame, text="Add layer", command=self.new_generator_kit)
        self.make_frame_btn.grid(row=2, column=0, padx=3, pady=3, sticky='nwe')

        # column 3 - array display area
        self.canvas = tk.Canvas(self, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg='black')
        # silly rowspan=500 - not to disturb placement of dynamic generator kits as it get's messy with low numbers
        self.canvas.grid(row=1, column=3, padx=5, pady=5, sticky='n')
        self.img = None
        self.map_img = self.canvas.create_image(2, 2, anchor='nw', image=self.img)

    def new_generator_kit(self):
        if len(self.dynamic_frames) < 5:
            generator_kit = GeneratorKit(self.col2_frame)
            self.dynamic_frames.append(generator_kit)
            self.group_generation_kits()

    def group_generation_kits(self):
        for i in range(len(self.dynamic_frames)):
            self.dynamic_frames[i].grid(row=i+1, column=0, pady=3, sticky='n')
        self.make_frame_btn.grid(row=len(self.dynamic_frames)+1)
        if len(self.dynamic_frames) > 4:
            self.make_frame_btn.grid_remove()

    def display_map(self):
        noise_map = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        for generator in self.dynamic_frames:
            if generator.noise_array is not None:
                noise_map += float(generator.factor_entry.get()) * generator.noise_array
        # normalize values to 0-levels
        if noise_map.ptp() != 0:
            noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp() * self.levels).astype(int)
            # rescale to 0-255 (grayscale)
            noise_map = noise_map / self.levels * 255
        if self.img is not None:
            self.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
            self.canvas.itemconfig(self.map_img, image=self.img)


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

