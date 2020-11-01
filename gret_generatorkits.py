from functools import partial
from gret_tkinter_widgets import *
from multiprocessing import cpu_count, Pool
from numpy import empty, array, shape, sqrt, amin
from noise import snoise2
from PIL import Image, ImageTk
from tkinter import Frame, Button, Scale, SUNKEN, HORIZONTAL


def generate_simplex_row(x, size, scale=100.0, octaves=6, persistence=0.5, base=0.0):
    """
    generate_simplex_row - function of generating one row of simplex noise.
    :param x: number of row, just for purposes of generation 2d array
    :param size: size of the main array, here it is size of the row
    :param scale: for controlling speed of changes in the array
    :param octaves: number of layers, each with more detail
    :param persistence: influence of each octave on the main one
    :param base: seed for the array generation (same seed - same output)
    :return: list of simplex noise values, of given size
    """
    noise_row = []
    x_scale = x / scale
    for y in range(size):
        noise_row.append(snoise2(x_scale, y / scale,
                                 octaves=octaves, persistence=persistence,
                                 base=base))
    return noise_row


class GeneratorKit(Frame):
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
        Frame.__init__(self, parent, relief='sunken', bd=1)
        self.root = parent.master

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)

        self.array = None

        # generator menu
        # base = seed for generator
        self.base_entry = LabeledEntry(self, text="Base: ", validate_for='int', value=0)
        self.base_entry.grid(row=0, column=0, sticky='e')
        # scale = how much to zoom in
        self.scale_entry = LabeledEntry(self, text="Scale: ", validate_for='int', value=400)
        self.scale_entry.grid(row=0, column=1, sticky='e')
        # octaves = number of layers of detail
        self.octaves_entry = LabeledEntry(self, text="Octaves: ", validate_for='int', value=6)
        self.octaves_entry.grid(row=0, column=2, sticky='e')
        # persistence = factor of contribution of higher octaves
        self.persistence_entry = LabeledEntry(self, text="Persistence: ", validate_for='float', value=0.5)
        self.persistence_entry.grid(row=1, column=0, columnspan=2, sticky='e')
        # factor = contribution of this array in the whole map
        self.factor_entry = LabeledEntry(self, text="Factor: ", validate_for='float', value=1)
        self.factor_entry.grid(row=1, column=2, sticky='e')

        self.generate_btn = Button(self, text="Generate", command=self.generate_array)
        self.generate_btn.grid(row=2, column=0, padx=5, pady=5, sticky='we')

        self.show_btn = Button(self, text="Show", command=self.show_array)
        self.show_btn.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        self.show_btn.grid_remove()

        self.destroy_btn = Button(self, text="Delete", command=self.self_destroy, bg='darkred', fg='lightgray')
        self.destroy_btn.grid(row=2, column=2, padx=5, pady=5, sticky='we')

    def generate_array(self, refresh_map=True):
        self.array = empty(self.root.MAP_SIZE, dtype=float)

        if cpu_count() > 6:
            p = Pool(6)
        else:
            p = Pool()
        simplex_row_partial = partial(generate_simplex_row,
                                      size=self.root.MAP_SIZE[1],
                                      scale=float(self.scale_entry.get()),
                                      octaves=int(self.octaves_entry.get()),
                                      persistence=float(self.persistence_entry.get()),
                                      base=float(self.base_entry.get()))
        list_tmp = p.map(simplex_row_partial, range(self.root.MAP_SIZE[0]))
        self.array = array(list_tmp)

        # normalize values to the range: 0-1
        if self.array.ptp():
            self.array = ((self.array - amin(self.array)) / self.array.ptp())

        if refresh_map:
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


class GradientKit(Frame):
    """
    Gradient Kit Frame - it manages gradient pattern.
    Gradient pattern allows modification of arrays.
    Parameters:
     - Minimum value gradient's radius: radius for max weakening of array's values
     - Maximum value gradient's radius: radius for max magnifying of array's values
    """
    def __init__(self, parent):
        Frame.__init__(self, parent, bd=1, relief=SUNKEN)
        self.root = parent.master

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)
        # basic array for faster response of changing pattern's parameters, but it takes 2x RAM!
        self.circle_basic_array = None
        self.array = None
        self.slider_events = ["<B1-Motion>",
                              "<ButtonRelease-1>",
                              "<B3-Motion>",
                              "<ButtonRelease-3>"]

        # gradient menu
        self.generate_btn = Button(self, text="Make gradient", command=self.generate_gradient)
        self.generate_btn.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        self.show_btn = Button(self, text="Show gradient", command=self.show_array)
        self.show_btn.grid(row=0, column=1, padx=5, pady=5, sticky='nw')
        self.show_btn.grid_remove()
        self.clear_btn = Button(self, text="Clear gradient",
                                command=self.clear_gradient, bg='darkred', fg='lightgray')
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5, sticky='nw')
        self.clear_btn.grid_remove()

        # sliders - radius range 0-1 where 0 is exact middle of array and 1 is the most far corner
        self.min_value_radius = Scale(self, from_=0, to=1, resolution=0.01, length=275,
                                      orient=HORIZONTAL, label="Minimum value gradient's radius")
        self.min_value_radius.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
        for event in self.slider_events:
            self.min_value_radius.bind(event, self.change_factor_event)
        self.max_value_radius = Scale(self, from_=0, to=1, resolution=0.01, length=275,
                                      orient=HORIZONTAL, label="Maximum value gradient's radius")
        self.max_value_radius.grid(row=2, column=0, padx=5, pady=5, columnspan=3)
        for event in self.slider_events:
            self.max_value_radius.bind(event, self.change_factor_event)
        self.max_value_radius.set(1)

    def change_factor_event(self, event):
        if self.array is not None:
            self.generate_gradient()

    def generate_gradient(self, refresh_map=True):
        if self.circle_basic_array is None \
                or shape(self.circle_basic_array)[0] != self.root.MAP_SIZE[0]\
                or shape(self.circle_basic_array)[1] != self.root.MAP_SIZE[1]:
            self.circle_basic_array = empty(self.root.MAP_SIZE, dtype=float)
            for i in range(self.root.MAP_SIZE[0] // 2):
                a = self.root.MAP_SIZE[0] // 2 - i
                for j in range(self.root.MAP_SIZE[1] // 2):
                    # old squared gradient formula: x = i if i < j else j
                    b = self.root.MAP_SIZE[1] // 2 - j
                    x = - sqrt(a*a + b*b)
                    self.circle_basic_array[i][j] = x
                    self.circle_basic_array[i][self.root.MAP_SIZE[1]-j-1] = x
                    self.circle_basic_array[self.root.MAP_SIZE[0]-i-1][j] = x
                    self.circle_basic_array[self.root.MAP_SIZE[0]-i-1][self.root.MAP_SIZE[1]-j-1] = x

        if self.max_value_radius.get() < self.min_value_radius.get():
            # allowing reversing gradient pattern (middle is suppressed instead of borders)
            self.array = 1 - self.circle_basic_array
        else:
            self.array = self.circle_basic_array.copy()

        # convert radius into array index
        x_of_border = int(self.root.MAP_SIZE[0] * (1 - self.max_value_radius.get()) / 2)
        y_of_border = int(self.root.MAP_SIZE[1] * (1 - self.max_value_radius.get()) / 2)
        self.array[self.array < self.array[x_of_border, y_of_border]] = \
            self.array[x_of_border, y_of_border]

        if self.max_value_radius.get() == self.min_value_radius.get():
            # in case of equal values, make sure indexes differ at least by 1 (pattern gets blank otherwise)
            x_of_border += 1
            y_of_border += 1
        else:
            x_of_border = int(self.root.MAP_SIZE[0] * (1 - self.min_value_radius.get()) / 2)
            y_of_border = int(self.root.MAP_SIZE[1] * (1 - self.min_value_radius.get()) / 2)

        self.array[self.array > self.array[x_of_border, y_of_border]] = \
            self.array[x_of_border, y_of_border]

        # normalize values to the range: 0-1
        if self.array.ptp():
            self.array = ((self.array - amin(self.array)) / self.array.ptp())

        if refresh_map:
            if self.root.img is None or self.root.displayed_frame is self:
                self.show_array()
            elif self.root.displayed_frame is self.root:
                self.root.display_map()

        self.show_btn.grid()
        self.clear_btn.grid()

    def show_array(self):
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
