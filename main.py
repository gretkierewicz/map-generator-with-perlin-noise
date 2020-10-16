import numpy as np
from opensimplex import OpenSimplex
import pgui
import pygame
import sys

pygame.init()


class Main:
    def __init__(self):
        self.SCREEN_HEIGHT = 840
        self.SCREEN_WIDTH = 1200
        self.MAP_SIZE = 800

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.widgets = []
        self.table = []
        self.noise = OpenSimplex()

        # test slider (length of screen - 10 - 10 - 15) last one is length of marker
        self.slider1 = pgui.Slider(self, orientation="horizontal", length=340, max=100)
        self.slider1.move(20, 20)
        self.slider1.set_mark(50)    # has to be set after .move (wth!?) otherwise does not works
        self.widgets.append(self.slider1)

        # test entry
        self.entry1 = pgui.Entry(self)
        self.entry1.move(20, 70)
        self.entry1.text = "50"
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

    def generate(self):
        x = np.arange(0, self.MAP_SIZE)
        y = np.arange(0, self.MAP_SIZE)
        X, Y = np.meshgrid(x, y)
        Z = X + Y
        for x in range(800):
            for y in range(800):
                Z[x][y] = 127 * (1 + self.noise.noise2d(x / (self.slider1.mark + 1) / int(self.entry1.text),
                                                        y / (self.slider1.mark + 1) / int(self.entry1.text)))
        surf = pygame.surfarray.make_surface(Z)
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

