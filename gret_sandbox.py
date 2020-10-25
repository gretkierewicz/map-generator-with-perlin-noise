import numpy as np
import tkinter as tk

from PIL import Image, ImageTk
from noise import snoise2


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


class LabeledEntry(tk.Frame):
    """
    LabelEntry - Supporting Frame of simple entries with labels
    Validation for INT and FLOAT included.
    """
    def __init__(self, parent, text="", validatefor='float', value=0.0):
        tk.Frame.__init__(self, parent)

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.VALIDATE_FLOAT = (self.register(validate_for_float), '%P')
        self.VALIDATE_INT = (self.register(validate_for_int), '%P')
        if validatefor == 'int':
            validatefor = self.VALIDATE_INT
        elif validatefor == 'float':
            validatefor = self.VALIDATE_FLOAT
        else:
            # allow no validation at all
            validatefor = None

        label = tk.Label(self, bg=self.main_bg, text=text)
        label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry = tk.Entry(self, width=5, validate='key', validatecommand=validatefor)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.entry.insert(0, value)

    def get(self):
        return self.entry.get()


class GeneratorKit(tk.Frame):
    """
    Generator Kit Frame - it manages creation of noise arrays.
    Noise array is created with help of simplex noise algorithm.
    Parameters of noise:
     - base: seed for algorithm, with same seed same base array will be created
     - scale: the bigger the scale the bigger magnitude of detail
     - octaves: number of levels of detail, less makes "smoothier" noise
     - persistence: how much every octave affects main one
    Other parameters:
     - factor: how much one array affects other arrays
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, relief='sunken', bd=1)
        self.root = parent.master

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.CANVAS_SIZE = 600
        self.array = None

        # generator menu
        # base = seed for generator
        self.base_entry = LabeledEntry(self, text="Base: ", validatefor='int', value=0)
        self.base_entry.grid(row=0, column=0, sticky='e')
        # scale = how much to zoom in
        self.scale_entry = LabeledEntry(self, text="Scale: ", validatefor='int', value=400)
        self.scale_entry.grid(row=0, column=1, sticky='e')
        # octaves = number of layers of detail
        self.octaves_entry = LabeledEntry(self, text="Octaves: ", validatefor='int', value=6)
        self.octaves_entry.grid(row=0, column=2, sticky='e')
        # persistence = factor of contribution of higher octaves
        self.persistence_entry = LabeledEntry(self, text="Persistence: ", validatefor='float', value=0.5)
        self.persistence_entry.grid(row=1, column=0, columnspan=2, sticky='e')
        # factor = contribution of this array in the whole map
        self.factor_entry = LabeledEntry(self, text="Factor: ", validatefor='float', value=1)
        self.factor_entry.grid(row=1, column=2, sticky='e')

        self.generate_btn = tk.Button(self, text="Generate", command=lambda: self.generate_array(
            base=float(self.base_entry.get()),
            scale=float(self.scale_entry.get()),
            octaves=int(self.octaves_entry.get()),
            persistence=float(self.persistence_entry.get())
        ))
        self.generate_btn.grid(row=2, column=0, padx=5, pady=5, sticky='we')

        self.show_btn = tk.Button(self, text="Show", command=self.show_array)
        self.show_btn.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        self.show_btn.grid_remove()

        self.destroy_btn = tk.Button(self, text="Delete", command=self.self_destroy, bg='darkred', fg='lightgray')
        self.destroy_btn.grid(row=2, column=2, padx=5, pady=5, sticky='we')

    def generate_array(self, base=0.0, scale=400.0, octaves=6, persistence=0.5):
        self.array = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        for x in range(self.CANVAS_SIZE):
            x_scale = x / scale
            for y in range(self.CANVAS_SIZE):
                self.array[x][y] = snoise2(x_scale, y / scale,
                                           octaves=octaves, persistence=persistence,
                                           repeatx=self.CANVAS_SIZE, repeaty=self.CANVAS_SIZE,
                                           base=base)

        # normalize values to the range: 0-1
        if self.array.ptp():
            self.array = ((self.array - np.amin(self.array)) / self.array.ptp())

        if self.root.img is None or self.root.displayed_frame is self:
            self.show_array()
        elif self.root.displayed_frame is self.root:
            self.root.display_map()

        self.show_btn.grid()

    def show_array(self):
        # normalize values to 0-levels and rescale to 0-255 (grayscale)
        noise_map = (self.array * self.root.levels).astype(int) / self.root.levels * 255
        self.root.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
        self.root.canvas.itemconfig(self.root.map_img, image=self.root.img)
        self.root.displayed_frame = self

    def self_destroy(self):
        self.root.dynamic_frames.remove(self)
        self.destroy()
        self.root.group_generation_kits()
        self.root.display_map()


class GradientKit(tk.Frame):
    """
    Gradient Kit Frame - it manages gradient pattern.
    Gradient pattern allows modification of arrays.
    Parameters:
     - Minimum value gradient's radius: radius for max weakening of array's values
     - Maximum value gradient's radius: radius for max magnifying of array's values
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=1, relief=tk.SUNKEN)
        self.root = parent.master

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)
        # basic array for faster response of changing pattern's parameters, but it takes 2x RAM!
        self.circle_basic_array = None
        self.array = None

        # gradient menu
        self.generate_btn = tk.Button(self, text="Make gradient", command=self.generate_gradient)
        self.generate_btn.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        self.show_btn = tk.Button(self, text="Show gradient", command=self.show_gradient)
        self.show_btn.grid(row=0, column=1, padx=5, pady=5, sticky='nw')
        self.show_btn.grid_remove()
        self.clear_btn = tk.Button(self, text="Clear gradient",
                                   command=self.clear_gradient, bg='darkred', fg='lightgray')
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5, sticky='nw')
        self.clear_btn.grid_remove()

        # sliders - radius range 0-1 where 0 is exact middle of array and 1 is the most far corner
        self.min_value_radius = tk.Scale(self, from_=0, to=1, resolution=0.01, length=275,
                                         orient=tk.HORIZONTAL, label="Minimum value gradient's radius")
        self.min_value_radius.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
        self.max_value_radius = tk.Scale(self, from_=0, to=1, resolution=0.01, length=275,
                                         orient=tk.HORIZONTAL, label="Maximum value gradient's radius")
        self.max_value_radius.grid(row=2, column=0, padx=5, pady=5, columnspan=3)
        self.max_value_radius.set(1)

    def generate_gradient(self):
        if self.circle_basic_array is None:
            self.circle_basic_array = np.empty((self.root.CANVAS_SIZE, self.root.CANVAS_SIZE), dtype=np.float)
            for i in range(self.root.CANVAS_SIZE // 2):
                a = self.root.CANVAS_SIZE // 2 - i
                for j in range(self.root.CANVAS_SIZE // 2):
                    # old squared gradient formula: x = i if i < j else j
                    b = self.root.CANVAS_SIZE // 2 - j
                    x = - np.sqrt(a*a + b*b)
                    self.circle_basic_array[i][j] = x
                    self.circle_basic_array[i][self.root.CANVAS_SIZE-j-1] = x
                    self.circle_basic_array[self.root.CANVAS_SIZE-i-1][j] = x
                    self.circle_basic_array[self.root.CANVAS_SIZE-i-1][self.root.CANVAS_SIZE-j-1] = x

        if self.max_value_radius.get() < self.min_value_radius.get():
            # allowing reversing gradient pattern (middle is suppressed instead of borders)
            self.array = np.copy(1 - self.circle_basic_array)
        else:
            self.array = np.copy(self.circle_basic_array)

        # convert radius into array index
        index_of_border = int(self.root.CANVAS_SIZE * (1 - self.max_value_radius.get()) / 2)
        self.array[self.array < self.array[index_of_border, index_of_border]] = \
            self.array[index_of_border, index_of_border]

        if self.max_value_radius.get() == self.min_value_radius.get():
            # in case of equal values, make sure indexes differ at least by 1 (pattern gets blank otherwise)
            index_of_border += 1
        else:
            index_of_border = int(self.root.CANVAS_SIZE * (1 - self.min_value_radius.get()) / 2)

        self.array[self.array > self.array[index_of_border, index_of_border]] = \
            self.array[index_of_border, index_of_border]

        # normalize values to the range: 0-1
        if self.array.ptp():
            self.array = ((self.array - np.amin(self.array)) / self.array.ptp())

        if self.root.img is None or self.root.displayed_frame is self:
            self.show_gradient()
        elif self.root.displayed_frame is self.root:
            self.root.display_map()

        self.show_btn.grid()
        self.clear_btn.grid()

    def show_gradient(self):
        # normalize values to 0-levels and rescale to 0-255 (grayscale)
        noise_map = (self.array * self.root.levels).astype(int) / self.root.levels * 255
        self.root.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
        self.root.canvas.itemconfig(self.root.map_img, image=self.root.img)
        self.root.displayed_frame = self

    def clear_gradient(self):
        self.show_btn.grid_remove()
        self.clear_btn.grid_remove()
        self.array = None
        self.root.display_map()


class Root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.title("gret_sandbox")
        #self.state('zoomed')
        self.geometry("1240x640")
        self.main_bg = "gray"
        self.config(bg=self.main_bg)

        # list of dynamically added/removed frames (generator kit frames for now)
        self.dynamic_frames = []
        # indicator of object of which array is actually displayed - for easy control of refreshing
        self.displayed_frame = None
        # canvas/array's size
        self.CANVAS_SIZE = 600
        # levels for better image visualization
        self.levels = 16

        # additional frames for proper placement purposes
        self.corner_offset = tk.Frame(self, width=10, height=10, bg=self.main_bg)
        self.corner_offset.grid(row=0, column=0)

        # column 1 - place for gradient and river generators
        self.col1_frame = tk.Frame(self, bg=self.main_bg)
        self.col1_frame.grid(row=1, column=1, sticky='n')
        # col_width frames are only to setup static width of frame (at least that is how I figured it out)
        self.col1_width = tk.Frame(self.col1_frame, width=300, bg=self.main_bg)
        self.col1_width.grid(row=0, column=0)
        # displaying the whole map button
        self.make_frame_btn = tk.Button(self.col1_frame, text="Display the whole map", command=self.display_map)
        self.make_frame_btn.grid(row=1, column=0, padx=3, pady=3, sticky='nwe')
        # create basic gradient kit
        self.gradient = GradientKit(self.col1_frame)
        self.gradient.grid(row=2, column=0, pady=3, sticky='n')

        # column 2 - generator kits
        self.col2_frame = tk.Frame(self, bg=self.main_bg)
        self.col2_frame.grid(row=1, column=2, sticky='n')
        self.col2_width = tk.Frame(self.col2_frame, width=300, bg=self.main_bg)
        self.col2_width.grid(row=0, column=0)
        # create basic generator kit
        generator_kit = GeneratorKit(self.col2_frame)
        # access generator kits by this list only - dynamic_frames
        self.dynamic_frames.append(generator_kit)
        generator_kit.grid(row=1, column=0, pady=3, sticky='n')
        # button for adding layers (generator kits, at least for now)
        self.make_frame_btn = tk.Button(self.col2_frame, text="Add layer", command=self.new_generator_kit)
        self.make_frame_btn.grid(row=2, column=0, padx=3, pady=3, sticky='nwe')

        # column 3 - array display area
        self.canvas = tk.Canvas(self, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg='black')
        self.canvas.grid(row=1, column=3, padx=5, pady=5, sticky='n')
        self.img = None
        self.map_img = self.canvas.create_image(2, 2, anchor='nw', image=self.img)

    # Create kit, add it to the list and run grouping method
    def new_generator_kit(self):
        # max number of kits controlled with showing/hiding "Add layer" button in grouping method
        generator_kit = GeneratorKit(self.col2_frame)
        self.dynamic_frames.append(generator_kit)
        self.group_generation_kits()

    # regrouping kits in case of creating new or deleting one
    def group_generation_kits(self):
        for i in range(len(self.dynamic_frames)):
            self.dynamic_frames[i].grid(row=i+1, column=0, pady=3, sticky='n')
        # Add layer button - always at the bottom of list
        self.make_frame_btn.grid(row=len(self.dynamic_frames)+1)
        # managing max number of kits, later on will be dependant of window size, or scrollbar will be added
        if len(self.dynamic_frames) > 4:
            self.make_frame_btn.grid_remove()

    # display all arrays, mixed together
    def display_map(self):
        noise_map = np.empty((self.CANVAS_SIZE, self.CANVAS_SIZE), dtype=np.float)
        for generator in self.dynamic_frames:
            if generator.array is not None:
                # the only place of using 'factor' parameter - it wages influence of each array
                noise_map += float(generator.factor_entry.get()) * generator.array
        if self.gradient.array is not None:
            noise_map *= self.gradient.array

        # normalize values to 0-levels
        if noise_map.ptp() != 0:
            noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp() * self.levels).astype(int)
            # rescale to 0-255 (grayscale)
            noise_map = noise_map / self.levels * 255
        else:
            self.img = None

        if self.img is not None:
            self.img = ImageTk.PhotoImage(image=Image.fromarray(noise_map))
            self.canvas.itemconfig(self.map_img, image=self.img)
            self.displayed_frame = self


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

