from noise import snoise2
from time import time
import numpy as np
import pgui
import pygame
import sys

pygame.init()


class Main:
    def __init__(self):
        self.SCREEN_HEIGHT = 880
        self.SCREEN_WIDTH = 1400
        self.MAP_SIZE = 800

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.widgets = []   # widget table for refresh purposes

        # octaves slider
        self.octaves_slider = pgui.Slider(self, orientation="horizontal", length=320, max=19)
        self.octaves_slider.move(10, 40)
        self.octaves_slider.set_width(25)
        self.octaves_slider.set_label("octaves")
        self.octaves_slider.set_font_size(26)
        self.octaves_slider.set_font("Calibri")
        self.octaves_slider.set_font_color((210, 210, 210, 0))  # 4-tuple this is a bug in pgui slider function
        self.octaves_slider.set_mark(6)     # has to be set after .move (wth!?) otherwise does not work
        self.widgets.append(self.octaves_slider)

        # octaves entry
        self.octaves_entry = pgui.Entry(self)
        self.octaves_entry.move(40 + self.octaves_slider.get_length(), 40)
        self.octaves_entry.max_length = 3
        self.widgets.append(self.octaves_entry)

        # Generate Button
        self.gen_btn = pgui.Button(self, width=100, height=40, func=self.generate, text="Generate")
        self.gen_btn.bg_color = (120, 120, 255)
        self.gen_btn.border_width = 3
        self.gen_btn.move(20, 150)
        self.widgets.append(self.gen_btn)

        # EXIT Button
        self.exit_btn = pgui.Button(self, width=60, height=40, func=sys.exit, text="Exit")
        self.exit_btn.bg_color = (255, 50, 50)
        self.exit_btn.border_width = 3
        self.exit_btn.move(20, self.SCREEN_HEIGHT - self.exit_btn.height - 20)
        self.widgets.append(self.exit_btn)

        self.screen.fill((70, 70, 70))

    def generate(self):
        start_time = time()
        noise_RGB = np.empty((self.MAP_SIZE, self.MAP_SIZE, 3), dtype=np.float)
        noise_map = np.empty((self.MAP_SIZE, self.MAP_SIZE), dtype=np.float)
        for x in range(self.MAP_SIZE):
            factor = 400
            x_factor = x / factor
            for y in range(self.MAP_SIZE):
                noise_map[x][y] = snoise2(x_factor, y / factor,
                                          octaves=self.octaves_slider.mark+1, persistence=0.5,
                                          repeatx=self.MAP_SIZE, repeaty=self.MAP_SIZE, base=0)

        noise_RGB[:, :, 0] = noise_RGB[:, :, 1] = noise_RGB[:, :, 2] = noise_map
        print("Generation time: %s" % (time() - start_time))
        number_of_levels = 16
        # normalize values to 0-number_of_levels
        noise_RGB = ((noise_RGB - np.amin(noise_map)) / noise_map.ptp() * number_of_levels).astype(int)
        # rescale to 0-255 (grayscale)
        noise_RGB = noise_RGB/ number_of_levels * 255

        surf = pygame.surfarray.make_surface(noise_RGB)
        # Update the screen
        self.screen.blit(surf, (self.SCREEN_WIDTH - self.MAP_SIZE - 20, 20))

    def update(self):
        for w in self.widgets:
            w.update()

        pygame.display.flip()
        self.clock.tick(200)

    def events(self):
        for event in pygame.event.get():
            # Exit if the window closing button is clicked
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
                if self.octaves_entry.text != str(self.octaves_slider.mark + 1):
                    self.octaves_entry.text = str(self.octaves_slider.mark + 1)
            # Exit if the 'Esc' key is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise SystemExit
                if event.key == pygame.K_RETURN:
                    if 0 < int(self.octaves_entry.text) < 20:
                        self.octaves_slider.set_mark(int(self.octaves_entry.text) - 1)
                    else:
                        self.octaves_entry.text = str(self.octaves_slider.mark + 1)


main = Main()
while True:
    main.update()
    main.events()

