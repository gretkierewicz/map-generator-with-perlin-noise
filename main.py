import numpy as np
from opensimplex import OpenSimplex
import pgui
import pygame
import sys
import multiprocessing

pygame.init()


class Main:
    def __init__(self):
        self.SCREEN_HEIGHT = 840
        self.SCREEN_WIDTH = 1200
        self.MAP_SIZE = 800

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.widgets = []   # widget table for refresh purposes
        self.noise = OpenSimplex()

        # test slider (length of screen - 10 - 10 - 15) last one is length of marker
        self.slider1 = pgui.Slider(self, orientation="horizontal", length=320, max=100)
        self.slider1.move(20, 20)
        self.slider1.set_mark(50)    # has to be set after .move (wth!?) otherwise does not work
        self.widgets.append(self.slider1)

        # test entry
        self.entry1 = pgui.Entry(self)
        self.entry1.move(20, 70)
        self.entry1.text = "1"
        self.widgets.append(self.entry1)

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

        # place empty (black) screen in place of noise map
        self.screen.blit(pygame.surfarray.make_surface(np.empty((self.MAP_SIZE, self.MAP_SIZE, 3), dtype=np.uint8)),
                         (self.SCREEN_WIDTH - self.MAP_SIZE - 20, 20))

    def generate(self):
        noise_map = np.empty((self.MAP_SIZE, self.MAP_SIZE, 3), dtype=np.float)
        for x in range(self.MAP_SIZE):
            for y in range(self.MAP_SIZE):
                noise_value = self.noise.noise2d(
                    x / (self.slider1.mark + 1) / float(self.entry1.text.replace(',', '.')),
                    y / (self.slider1.mark + 1) / float(self.entry1.text.replace(',', '.')))
                noise_map[x][y] = [noise_value, noise_value, noise_value]
        number_of_levels = 8
        # normalize values to 0-number_of_levels
        noise_map = ((noise_map - np.amin(noise_map)) / noise_map.ptp() * number_of_levels).astype(int)
        # rescale to 0-255 (grayscale)
        noise_map = noise_map / number_of_levels * 255
        surf = pygame.surfarray.make_surface(noise_map)

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
            # Exit if the 'Esc' key is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise SystemExit


main = Main()
while True:
    main.update()
    main.events()

