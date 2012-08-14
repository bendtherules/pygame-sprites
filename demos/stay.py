#!/usr/bin/env python

import os
import pygame
from pygame.locals import *
from pygame.compat import geterror

# Import new sprite class
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from sprite import *

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

SCREEN_SIZE = 700
SCREEN_CENTER = (SCREEN_SIZE / 2, SCREEN_SIZE / 2)
SCALE_STEP = 0.1
SCALE_MIN = 0.3
SCALE_MAX = 7.0
ROTATE_STEP = 5

colors = {
        "background": pygame.Color(225, 225, 225),
        "square": pygame.Color(0, 0, 0)
}


def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


def draw_squares(screen):
    line_length = 5
    for size in [100, 250, 500]:
        for sgn_x in [+1, -1]:
            for sgn_y in [+1, -1]:
                x = SCREEN_SIZE / 2 + sgn_x * size / 2
                y = SCREEN_SIZE / 2 + sgn_y * size / 2
                pygame.draw.lines(screen, colors["square"], False,
                        [(x, y - sgn_y * line_length),
                         (x, y),
                         (x - sgn_x * line_length, y)])


class Ball(Sprite):
    def __init__(self):
        Sprite.__init__(self)
        self.set_image(load_image("ball.png", -1))
        self.anchor = ANCHOR_CENTER


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    clock = pygame.time.Clock()
    scale_keys = [pygame.K_UP, pygame.K_DOWN]
    rotate_keys = [pygame.K_RIGHT, pygame.K_LEFT]
    visibility_keys = [pygame.K_SPACE]
    anchor_keys = [pygame.K_a]
    quit_keys = [pygame.K_ESCAPE, pygame.K_q]

    # background
    background = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
    background = background.convert()
    background.fill(colors["background"])

    # add ball sprite
    ball = Ball()
    ball.move_to(SCREEN_CENTER)
    all = Group((ball))

    scale, rotate = 0, 0
    try:
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        scale = 1
                    elif event.key == pygame.K_DOWN:
                        scale = -1
                    elif event.key == pygame.K_LEFT:
                        rotate = 1
                    elif event.key == pygame.K_RIGHT:
                        rotate = -1
                elif event.type == pygame.KEYUP:
                    if event.key in scale_keys:  # reset scale
                        scale = 0
                    elif event.key in rotate_keys:  # reset rotate
                        rotate = 0
                    elif event.key in anchor_keys:  # toggle anchor
                        if ball.anchor == ANCHOR_CENTER:
                            ball.anchor = ANCHOR_TOPLEFT
                        else:
                            ball.anchor = ANCHOR_CENTER
                    elif event.key in visibility_keys:
                        ball.toggle_visibility()
                    elif event.key in quit_keys:  # quit game
                        return

            if scale != 0:
                new_scale = ball.scale + SCALE_STEP * scale
                if SCALE_MIN < new_scale < SCALE_MAX:
                    ball.scale_by(scale * SCALE_STEP)

            if rotate != 0:
                ball.rotate_by(rotate * ROTATE_STEP)

            all.clear(screen, background)
            all.update()

            screen.blit(background, (0, 0))
            draw_squares(screen)

            all.draw(screen)
            pygame.display.flip()
            clock.tick(40)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
