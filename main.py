import numpy
import opensimplex
import pgui
import pygame
import sys

pygame.init()


class Main:
    def __init__(self):
        SCREEN_HEIGHT = 800
        SCREEN_WIDTH = 1600

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.widgets = []

        # EXIT Button
        self.exit_btn = pgui.Button(self, width=60, height=40, func=sys.exit, text="Exit")
        self.exit_btn.bg_color = (255, 50, 50)
        self.exit_btn.border_width = 3
        self.exit_btn.move(SCREEN_WIDTH - self.exit_btn.width - 20, SCREEN_HEIGHT - self.exit_btn.height - 20)
        self.widgets.append(self.exit_btn)

        # test slider (length of screen - 10 - 10 - 15) last one is length of marker
        self.slider = pgui.Slider(self, orientation="horizontal", length=SCREEN_WIDTH - 35, max=100)
        self.slider.move(10, 10)
        self.slider.set_mark(50)    # has to be set after .move (wth!?) otherwise does not works
        self.widgets.append(self.slider)

        # test entry
        self.entry = pgui.Entry(self)
        self.entry.move(10, 40)
        self.widgets.append(self.entry)

    def update(self):
        self.screen.fill((70, 70, 70))

        if self.entry.text != str(self.slider.mark):
            self.entry.text = str(self.slider.mark)

        for w in self.widgets:
            w.update()

        # Update the screen
        pygame.display.flip()

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

