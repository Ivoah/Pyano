import pygame
import random

TIME_SCALE = 5

channel_colors = [
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xe8, 0x73), (0xff, 0xd4, 0x3b)),
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98))
]

# channel_colors = [random.sample(range(0xff), 3) for channel in range(16)]

def fill_gradient(surface, c1, c2, rect=None):
    lerp = lambda a, b, r: a + (b - a)*r

    if type(rect) is tuple: rect = pygame.Rect(*rect)
    elif rect is None: rect = surface.get_rect()

    for column in range(rect.width):
        c = (
            lerp(c1[0], c2[0], column/rect.width),
            lerp(c1[1], c2[1], column/rect.width),
            lerp(c1[2], c2[2], column/rect.width)
        )
        pygame.draw.line(surface, c, (rect.left + column, rect.top), (rect.left + column, rect.bottom))

def border_box(size, border, col1, col2=(0, 0, 0)):
    s = pygame.Surface(size)
    s.fill(col2)
    if len(col1) == 2:
        fill_gradient(s, col1[0], col1[1], pygame.Rect(border, border, size[0] - 2*border, size[1] - 2*border))
    elif len(col1) == 3:
        s.fill(col1, (border, border, size[0] - 2*border, size[1] - 2*border))
    else:
        raise ValueError('col1 must be a color or tuple containing 2 colors')
    return s

whites = [0, 2, 4, 5, 7, 9, 11]
blacks = [1, 3, 6, 8, 10]

def key_pos(key):
    key %= 12
    if key in whites:
        return whites.index(key)/len(whites)
    else:
        return key/12

def key_width(key):
    key %= 12
    if key in whites:
        return 1/len(whites)
    else:
        return 1/12

def draw_octaves(size, octaves, highlight={}):
    s = pygame.Surface(size)
    octave_range = octaves[1] - octaves[0]
    for octave in range(*octaves):
        for i, key in enumerate(whites):
            width = size[0]/(7*octave_range)
            rect = ((i + (octave - octaves[0])*7)*width, 0, width, size[1])
            if key + octave*12 in highlight:
                box = border_box(rect[2:], 3, channel_colors[highlight[key + octave*12]])
                s.blit(box, rect[:2])
            else:
                pygame.draw.rect(s, (255, 255, 255), rect)
                pygame.draw.rect(s, (0, 0, 0), rect, 3)
        for i, key in enumerate(blacks):
            width = size[0]/(12*octave_range)
            rect = ((key + (octave - octaves[0])*12)*width, 0, width, size[1]*2/3)
            if key + octave*12 in highlight:
                box = border_box(rect[2:], 3, channel_colors[highlight[key + octave*12]])
                s.blit(box, rect[:2])
            else:
                pygame.draw.rect(s, (0, 0, 0), rect)
                pygame.draw.rect(s, (0, 0, 0), rect, 3)
    return s

def note_visible(note, time, vh):
    return note['stop'] > time and (note['start'] - time)/TIME_SCALE < vh
