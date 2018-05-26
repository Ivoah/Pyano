import pygame

def fill_gradient(surface, c1, c2, rect=None):
    lerp = lambda a, b, r: a + (b - a)*r

    if rect is None: rect = surface.get_rect()

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

def draw_octave(size, octave, highlights=[]):
    s = pygame.Surface(size)
    for key in whites:
        key_surf = border_box((size[0]*key_width(key), size[1]), 5, col1=(255, 255, 224) if key + octave*12 in highlights else (255, 255, 255))
        s.blit(key_surf, (size[0]*key_pos(key), 0))
    for key in blacks:
        key_surf = border_box((size[0]*key_width(key), size[1]*2/3), 5, col1=(255, 255, 224) if key + octave*12 in highlights else (0, 0, 0))
        s.blit(key_surf, (size[0]*key_pos(key), 0))
    return s
