import multiprocessing as mp
import numpy as np
import time
import tkinter as tk

from noise import snoise2
from functools import partial
from PIL import Image, ImageTk


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


def convert_heightmap_into_RGB(heightmap, level_1=0.3, level_2=0.5, level_3=0.5, brightness=1):
    """
    convert_heightmap_into_RGB - supportive function
    :param heightmap: 2D heightmap
    :param level_1: absolute seashore level (range from 0.01 to 0.99)
    :param level_2: relative (above seashore) plains level (range from 0.01 to 0.99)
    :param level_3: relative (above plains) hills level (range from 0.01 to 0.99)
    :param brightness: brightness of colors for output (range from 0 to 1)
    :return: 2D array of same size as heightmap, with RGB arguments ([R, G, B])
    """
    array_shape = np.shape(heightmap)
    if array_shape[0] < 10 or array_shape[1] < 10:
        return None
    # not perfect, but that assures that this function will work properly
    if level_1 < 0.01:  level_1 = 0.01
    if level_1 > 0.99:  level_1 = 0.99
    if level_2 < 0.01:  level_2 = 0.01
    if level_2 > 0.99:  level_2 = 0.99
    if level_3 < 0.01:  level_3 = 0.01
    if level_3 > 0.99:  level_3 = 0.99
    if brightness < 0:  brightness = 0
    if brightness > 1:  brightness = 1

    RGB_map = np.ones((array_shape[0], array_shape[1], 3), dtype=np.float)
    sea_level = level_1
    plains_level = level_2 * (1 - sea_level) + sea_level
    hills_level = level_3 * (1 - plains_level) + plains_level
    """
    Topology basic colors and levels for sea (from bottom to seashore):
    RED     ->  rises from middle of scale twice as fast as heightmap
    GREEN   ->  rises from bottom to seashore with normal rate of heightmap
    BLUE    ->  rises from start to middle twice as fast as heightmap 
    """
    # GREEN
    tmp_map = np.copy(heightmap)
    tmp_map[heightmap > sea_level] = sea_level
    tmp_map = ((tmp_map - np.amin(tmp_map)) / tmp_map.ptp())
    RGB_map[:, :, 1] = tmp_map
    # RED
    tmp_map = tmp_map * 2 - 1
    tmp_map[tmp_map < 0] = 0
    RGB_map[:, :, 0] = tmp_map
    # BLUE
    tmp_map = RGB_map[:, :, 1] * 2
    tmp_map[tmp_map > 1] = 1
    tmp_map[heightmap >= sea_level] = 0
    RGB_map[:, :, 2] = tmp_map * brightness * 255
    """
    Topology basic colors and levels for land:
    Seashore: RED = 0, GREEN = 1, BLUE = 0
    Elevations:
    seashore-1: GREEN -> 1 | 1-2: RED -> 1 | 2-max: GREEN -> 0
    """
    # RED plains_level - hills_level
    tmp_map = np.copy(heightmap)
    tmp_map[tmp_map < plains_level] = plains_level
    tmp_map[tmp_map > hills_level] = hills_level
    tmp_map = ((tmp_map - np.amin(tmp_map)) / tmp_map.ptp())
    tmp_map[heightmap < sea_level] = 1
    RGB_map[:, :, 0] = RGB_map[:, :, 0] * tmp_map * brightness * 255
    # GREEN hills_level+
    tmp_map = np.copy(heightmap)
    tmp_map[tmp_map < hills_level] = hills_level
    tmp_map = ((tmp_map - np.amin(tmp_map)) / tmp_map.ptp()) * 0.8
    RGB_map[:, :, 1] = RGB_map[:, :, 1] * (0.8 - tmp_map)
    # GREEN seashore - 1
    tmp_map = np.copy(heightmap)
    tmp_map[tmp_map < sea_level] = sea_level
    tmp_map[tmp_map > hills_level] = hills_level
    tmp_map = ((tmp_map - np.amin(tmp_map)) / tmp_map.ptp())
    tmp_map[heightmap < sea_level] = 1
    RGB_map[:, :, 1] = RGB_map[:, :, 1] * tmp_map * brightness * 255
    # BLUE - no blue for land!

    return RGB_map.astype(np.uint8)


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


class LabeledVerticalScale(tk.Frame):
    """
    LabeledVerticalScale - Supporting Frame of vertical slider with labels
    """
    def __init__(self, parent, text="", value=0.0, slider_func=None):
        tk.Frame.__init__(self, parent)

        self.main_bg = parent['bg']
        self.config(bg=self.main_bg)
        self.slider_events = ["<ButtonRelease-1>",
                              "<ButtonRelease-3>"]

        label = tk.Label(self, text=text)
        label.grid(row=0, column=0, padx=5, pady=3, sticky='s')
        self.slider = tk.Scale(self, from_=0.99, to=0.01, orient=tk.VERTICAL,
                               resolution=0.05, length=200, width=18)
        self.slider.grid(row=1, column=0, padx=5, pady=5, sticky='n')
        for event in self.slider_events:
            self.slider.bind(event, slider_func)
        self.slider.set(value)
        label.config(bg=self.slider['bg'])

    def get(self):
        return self.slider.get()


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

        self.generate_btn = tk.Button(self, text="Generate", command=self.generate_array)
        self.generate_btn.grid(row=2, column=0, padx=5, pady=5, sticky='we')

        self.show_btn = tk.Button(self, text="Show", command=self.show_array)
        self.show_btn.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        self.show_btn.grid_remove()

        self.destroy_btn = tk.Button(self, text="Delete", command=self.self_destroy, bg='darkred', fg='lightgray')
        self.destroy_btn.grid(row=2, column=2, padx=5, pady=5, sticky='we')

    def generate_array(self, refresh_map=True):
        self.array = np.empty(self.root.MAP_SIZE, dtype=np.float)

        if mp.cpu_count() > 6:
            p = mp.Pool(6)
        else:
            p = mp.Pool()
        simplex_row_partial = partial(generate_simplex_row,
                                       size=self.root.MAP_SIZE[1],
                                       scale=float(self.scale_entry.get()),
                                       octaves=int(self.octaves_entry.get()),
                                       persistence=float(self.persistence_entry.get()),
                                       base=float(self.base_entry.get()))
        #start_time = time.time()
        list_tmp = p.map(simplex_row_partial, range(self.root.MAP_SIZE[0]))
        #print("GeneratorKit array generation time:  %.4f seconds" % (time.time() - start_time))
        self.array = np.array(list_tmp)

        # normalize values to the range: 0-1
        if self.array.ptp():
            self.array = ((self.array - np.amin(self.array)) / self.array.ptp())

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
        self.slider_events = ["<B1-Motion>",
                              "<ButtonRelease-1>",
                              "<B3-Motion>",
                              "<ButtonRelease-3>"]

        # gradient menu
        self.generate_btn = tk.Button(self, text="Make gradient", command=self.generate_gradient)
        self.generate_btn.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        self.show_btn = tk.Button(self, text="Show gradient", command=self.show_array)
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
        for event in self.slider_events:
            self.min_value_radius.bind(event, self.change_factor_event)
        self.max_value_radius = tk.Scale(self, from_=0, to=1, resolution=0.01, length=275,
                                         orient=tk.HORIZONTAL, label="Maximum value gradient's radius")
        self.max_value_radius.grid(row=2, column=0, padx=5, pady=5, columnspan=3)
        for event in self.slider_events:
            self.max_value_radius.bind(event, self.change_factor_event)
        self.max_value_radius.set(1)

    def change_factor_event(self, event):
        if self.array is not None:
            self.generate_gradient()

    def generate_gradient(self, refresh_map=True):
        #start_time = time.time()
        if self.circle_basic_array is None \
                or np.shape(self.circle_basic_array)[0] != self.root.MAP_SIZE[0]\
                or np.shape(self.circle_basic_array)[1] != self.root.MAP_SIZE[1]:
            self.circle_basic_array = np.empty(self.root.MAP_SIZE, dtype=np.float)
            for i in range(self.root.MAP_SIZE[0] // 2):
                a = self.root.MAP_SIZE[0] // 2 - i
                for j in range(self.root.MAP_SIZE[1] // 2):
                    # old squared gradient formula: x = i if i < j else j
                    b = self.root.MAP_SIZE[1] // 2 - j
                    x = - np.sqrt(a*a + b*b)
                    self.circle_basic_array[i][j] = x
                    self.circle_basic_array[i][self.root.MAP_SIZE[1]-j-1] = x
                    self.circle_basic_array[self.root.MAP_SIZE[0]-i-1][j] = x
                    self.circle_basic_array[self.root.MAP_SIZE[0]-i-1][self.root.MAP_SIZE[1]-j-1] = x

        if self.max_value_radius.get() < self.min_value_radius.get():
            # allowing reversing gradient pattern (middle is suppressed instead of borders)
            self.array = np.copy(1 - self.circle_basic_array)
        else:
            self.array = np.copy(self.circle_basic_array)

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
            self.array = ((self.array - np.amin(self.array)) / self.array.ptp())

        if refresh_map:
            if self.root.img is None or self.root.displayed_frame is self:
                self.show_array()
            elif self.root.displayed_frame is self.root:
                self.root.display_map()

        self.show_btn.grid()
        self.clear_btn.grid()
        #print("Gradient array generation time:  %.4f seconds" % (time.time() - start_time))

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


class Root(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.title("gret_sandbox")
        self.minsize(1150, 550)
        self.geometry("1440x840")
        self.main_bg = "gray"
        self.config(bg=self.main_bg)
        self.update()
        self.bind("<Configure>", self.window_resize_event)

        # list of dynamically added/removed frames (generator kit frames for now)
        self.dynamic_frames = []
        # indicator of object of which array is actually displayed - for easy control of refreshing
        self.displayed_frame = None
        # canvas' size (height, width) - to be the same as for MAP_SIZE
        self.CANVAS_SIZE = (0, 0)
        # array's size (rows, columns) => (height, width)
        self.MAP_SIZE = (800, 800)
        # levels for better image visualization
        self.levels = 24

        # additional frame for proper placement purposes
        self.corner_offset = tk.Frame(self, width=10, height=10, bg=self.main_bg)
        self.corner_offset.grid(row=0, column=0)

        # column 1 - place for gradient and river generators
        self.col1_frame = tk.Frame(self, bg=self.main_bg)
        self.col1_frame.grid(row=1, column=1, sticky='n')
        # col_width frames are only to setup static width of frame (at least that is how I figured it out)
        self.col1_width = tk.Frame(self.col1_frame, width=300, bg=self.main_bg)
        self.col1_width.grid(row=0, column=0)
        # create basic gradient kit
        self.gradient = GradientKit(self.col1_frame)
        self.gradient.grid(row=2, column=0, pady=3, sticky='n')

        # Map controls frame
        self.map_frame = tk.Frame(self.col1_frame, bg=self.main_bg, bd=1, relief=tk.SUNKEN)
        self.map_frame.grid(row=3, column=0, pady=3, sticky='n')
        self.map_frame_width = tk.Frame(self.map_frame, width=292, bg=self.main_bg)
        self.map_frame_width.grid(row=0, column=0, columnspan=5)
        # sea level slider
        self.sea_level_slider = LabeledVerticalScale(self.map_frame,
                                                     text="Sea level", value=0.3,
                                                     slider_func=self.change_map_level_event)
        self.sea_level_slider.grid(row=0, column=0, padx=5, pady=3)
        # plains slider
        self.plains_level_slider = LabeledVerticalScale(self.map_frame,
                                                        text="Plains level", value=0.5,
                                                        slider_func=self.change_map_level_event)
        self.plains_level_slider.grid(row=0, column=1, padx=5, pady=3)
        # hills slider
        self.hills_level_slider = LabeledVerticalScale(self.map_frame,
                                                       text="Hills level", value=0.5,
                                                       slider_func=self.change_map_level_event)
        self.hills_level_slider.grid(row=0, column=2, padx=5, pady=3)
        # resize map frame
        self.resize_map_frame = tk.Frame(self.map_frame, bg=self.main_bg)
        self.resize_map_frame.grid(row=1, column=0, padx=5, columnspan=4, sticky='we')
        self.map_width_entry = LabeledEntry(self.resize_map_frame, text="Map width: ",
                                            validatefor='int', value=self.MAP_SIZE[0])
        self.map_width_entry.grid(row=1, column=0, columnspan=2, sticky='w')
        self.map_height_entry = LabeledEntry(self.resize_map_frame, text="height: ",
                                             validatefor='int', value=self.MAP_SIZE[1])
        self.map_height_entry.grid(row=1, column=2, columnspan=2, sticky='w')
        self.resize_arrays_btn = tk.Button(self.resize_map_frame, text="Apply", width=7, command=self.resize_arrays)
        self.resize_arrays_btn.grid(row=1, column=4, sticky='e')
        # displaying the whole map button
        self.make_frame_btn = tk.Button(self.map_frame, text="Display the whole map", command=self.display_map)
        self.make_frame_btn.grid(row=2, column=0, padx=3, pady=3, columnspan=5, sticky='nwe')

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
        self.canvas_frame = tk.Frame(self, bg=self.main_bg)
        self.canvas_frame.grid(row=1, column=3)
        self.canvas = tk.Canvas(self.canvas_frame, scrollregion=(0, 0, self.MAP_SIZE[1], self.MAP_SIZE[0]),
                                width=self.CANVAS_SIZE[1], height=self.CANVAS_SIZE[0], bg='black')
        self.canvas.grid(row=0, column=0, sticky='nw')
        self.img = None
        self.map_img = self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        # scrollbars for canvas
        self.canvas_side_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.canvas_side_scrollbar.grid(row=0, column=1, sticky='ns')
        self.canvas_side_scrollbar.config(command=self.canvas.yview)
        self.canvas_bottom_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.canvas_bottom_scrollbar.grid(row=1, column=0, sticky='we')
        self.canvas_bottom_scrollbar.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.canvas_side_scrollbar.set,
                           xscrollcommand=self.canvas_bottom_scrollbar.set)
        # some additional bind for drag and drop the canvas
        self.canvas.bind('<Button-1>', lambda event: self.canvas.scan_mark(event.x // 10, event.y // 10))
        self.canvas.bind('<B1-Motion>', lambda event: self.canvas.scan_dragto(event.x // 10, event.y // 10))

    def change_map_level_event(self, event):
        if self.displayed_frame is self:
            self.display_map()

    def window_resize_event(self, event):
        save_width = 640
        save_height = 40
        if self.CANVAS_SIZE[1] != self.winfo_width() - save_width \
                or self.CANVAS_SIZE[0] != self.winfo_height() - save_height:
            self.CANVAS_SIZE = (self.winfo_height() - save_height, self.winfo_width() - save_width)
            self.canvas.configure(width=self.CANVAS_SIZE[1], height=self.CANVAS_SIZE[0])
            #print(self.CANVAS_SIZE)

    def resize_arrays(self):
        if int(self.map_height_entry.get()) < 400:
            self.map_height_entry.entry.delete(0, tk.END)
            self.map_height_entry.entry.insert(0, 400)
        if int(self.map_width_entry.get()) < 400:
            self.map_width_entry.entry.delete(0, tk.END)
            self.map_width_entry.entry.insert(0, 400)
        self.MAP_SIZE = (int(self.map_height_entry.get()), int(self.map_width_entry.get()))
        self.canvas.config(scrollregion=(0, 0, self.MAP_SIZE[1], self.MAP_SIZE[0]))
        for generator in self.dynamic_frames:
            if generator.array is not None:
                generator.generate_array(refresh_map=False)
        if self.gradient.array is not None:
            self.gradient.generate_gradient(refresh_map=False)
        try:
            self.displayed_frame.show_array()
        except AttributeError:
            self.display_map()

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
        noise_map = np.empty(self.MAP_SIZE, dtype=np.float)
        for generator in self.dynamic_frames:
            if generator.array is not None:
                # the only place of using 'factor' parameter - it wages influence of each array
                noise_map += float(generator.factor_entry.get()) * generator.array

        # normalize values to 0-levels
        if noise_map.ptp() != 0:
            if self.gradient.array is not None:
                noise_map *= self.gradient.array
                noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp())
            noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp() * self.levels).astype(int)
            # rescale to 0-1 for colorful topology map
            noise_map = noise_map / self.levels
        else:
            self.img = None

        if self.img is not None:
            self.img = ImageTk.PhotoImage(image=Image.fromarray(
                convert_heightmap_into_RGB(noise_map,
                                           self.sea_level_slider.get(),
                                           self.plains_level_slider.get(),
                                           self.hills_level_slider.get())))
            self.canvas.itemconfig(self.map_img, image=self.img)
            self.displayed_frame = self


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

