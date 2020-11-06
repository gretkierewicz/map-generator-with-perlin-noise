import numpy as np
import tkinter as tk

from gret_convert import *
from gret_generatorkits import *
from gret_tkinter_widgets import *
from PIL import Image, ImageTk


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
        self.levels = 32

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
                                                     slider_bind_func=self.change_map_level_event)
        self.sea_level_slider.grid(row=0, column=0, padx=5, pady=3)
        # plains slider
        self.plains_level_slider = LabeledVerticalScale(self.map_frame,
                                                        text="Plains level", value=0.5,
                                                        slider_bind_func=self.change_map_level_event)
        self.plains_level_slider.grid(row=0, column=1, padx=5, pady=3)
        # hills slider
        self.hills_level_slider = LabeledVerticalScale(self.map_frame,
                                                       text="Hills level", value=0.5,
                                                       slider_bind_func=self.change_map_level_event)
        self.hills_level_slider.grid(row=0, column=2, padx=5, pady=3)
        # resize map frame
        self.resize_map_frame = tk.Frame(self.map_frame, bg=self.main_bg)
        self.resize_map_frame.grid(row=1, column=0, padx=5, columnspan=4, sticky='we')
        self.map_width_entry = LabeledEntry(self.resize_map_frame, text="Map width: ",
                                            validate_for='int', value=self.MAP_SIZE[0])
        self.map_width_entry.grid(row=1, column=0, columnspan=2, sticky='w')
        self.map_height_entry = LabeledEntry(self.resize_map_frame, text="height: ",
                                             validate_for='int', value=self.MAP_SIZE[1])
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
            noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp() * self.levels).astype(int)
            # rescale to 0-1 for colorful topology map
            noise_map = noise_map / self.levels
        else:
            self.img = None

        if self.img is not None:
            self.img = ImageTk.PhotoImage(image=Image.fromarray(
                convert_heightmap_into_RGB(noise_map, levels=[self.sea_level_slider.get(),
                                                              self.plains_level_slider.get(),
                                                              self.hills_level_slider.get()]
                                           )))
            self.canvas.itemconfig(self.map_img, image=self.img)
            self.displayed_frame = self


if __name__ == "__main__":
    root = Root(None)
    root.mainloop()

