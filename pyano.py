import pygame
import pygame.midi

from pygame.locals import *

KEY_DOWN = 144
KEY_UP = 128

TIME_SCALE = 5

whites = [0, 2, 4, 5, 7, 9, 11]
blacks = [1, 3, 6, 8, 10]

pygame.init()
pygame.midi.init()

def border_box(size, border, col1=(255, 255, 255), col2=(0, 0, 0)):
    s = pygame.Surface(size)
    s.fill(col2)
    s.fill(col1, (border, border, size[0] - 2*border, size[1] - 2*border))
    return s

def key_pos(key):
    if key in whites:
        return whites.index(key)/len(whites)
    else:
        return key/12

def key_width(key):
    if key in whites:
        return 1/len(whites)
    else:
        return 1/12

def draw_octave(size, highlights=[]):
    s = pygame.Surface(size)
    for key in whites:
        key_surf = border_box((size[0]*key_width(key), size[1]), 5, col1=(255, 255, 224) if key in highlights else (255, 255, 255))
        s.blit(key_surf, (size[0]*key_pos(key), 0))
    for key in blacks:
        key_surf = border_box((size[0]*key_width(key), size[1]*2/3), 5, col1=(255, 255, 224) if key in highlights else (0, 0, 0))
        s.blit(key_surf, (size[0]*key_pos(key), 0))
    return s

window = pygame.display.set_mode((640, 480))
print(f'Using {pygame.midi.get_device_info(pygame.midi.get_default_input_id())}')
keyb = pygame.midi.Input(pygame.midi.get_default_input_id())

notes_played = []

try:
    running = True
    while running:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.mod == 1024 and event.key == 113) or event.type == QUIT:
                running = False

        if keyb.poll():
            msg, time = keyb.read(1)[0]
            print(msg)
            note = msg[1] - 60
            if msg[0] == KEY_DOWN:
                #notes_played.append([note, time, None])
                notes_played.append([note, pygame.midi.time(), None])
            elif msg[0] == KEY_UP:
                for n in notes_played:
                    if n[0] == note and n[2] is None:
                        n[2] = pygame.midi.time()

        window.fill((0, 255, 255))
        window.blit(draw_octave((640, 480/3), [note[0] for note in notes_played if note[2] is None]), (0, 480*2/3))

        hit_list = []
        for note in sorted(notes_played, key=lambda n: n[1]):
            if note[2] is not None and note[2] < (pygame.midi.time() - (480*2/3)*TIME_SCALE): hit_list.append(note)
            s = border_box((key_width(note[0])*640, ((note[2] or pygame.midi.time()) - note[1])/TIME_SCALE), 5, col1=(255, 255, 224))
            window.blit(s, (key_pos(note[0])*640, 480*2/3 + (note[1] - pygame.midi.time())/TIME_SCALE))

        for note in hit_list:
            notes_played.remove(note)

        pygame.display.update()
finally:
    keyb.close()
    pygame.midi.quit()
    pygame.quit()