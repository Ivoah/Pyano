#!/usr/bin/env python3

import mido
import pygame
import pygame.time

from pygame.locals import *

TIME_SCALE = 5

whites = [0, 2, 4, 5, 7, 9, 11]
blacks = [1, 3, 6, 8, 10]

pygame.init()

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
keyb = mido.open_input()
clock = pygame.time.Clock()

midi_file = mido.MidiFile('Still Alive.mid')
song = []
pending_notes = {}
cur_time = 0
for msg in midi_file:
    if msg.is_meta:
        continue

    cur_time += msg.time
    if msg.type == 'note_on' and msg.velocity > 0:
        pending_notes[(msg.channel, msg.note)] = cur_time
    elif msg.type == 'note_off' or msg.type == 'note_on' and msg.velocity == 0:
        song.append({
            'note': msg.note,
            'channel': msg.channel,
            'start': pending_notes[(msg.channel, msg.note)]*1000,
            'stop': cur_time*1000
        })

song = sorted(song, key=lambda note: note['start'])

notes_played = []

try:
    running = True
    while running:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.mod == 1024 and event.key == 113) or event.type == QUIT:
                running = False

        msg = keyb.poll()
        if msg:
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_played.append({
                    'note': msg.note - 60,
                    'channel': msg.channel,
                    'start': pygame.time.get_ticks(),
                    'stop': None
                })
            elif msg.type == 'note_off' or msg.type == 'note_on' and msg.velocity == 0:
                for note in notes_played:
                    if note['note'] == msg.note - 60 and note['stop'] is None:
                        note['stop'] = pygame.time.get_ticks()

        window.fill((0, 255, 255))
        window.blit(draw_octave((640, 480/3), [note['note'] for note in notes_played if note['stop'] is None]), (0, 480*2/3))

        hit_list = []
        for note in sorted(notes_played, key=lambda n: n['start']):
            if note['stop'] is not None and note['stop'] < (pygame.time.get_ticks() - (480*2/3)*TIME_SCALE): hit_list.append(note)
            s = border_box((key_width(note['note'])*640, ((note['stop'] or pygame.time.get_ticks()) - note['start'])/TIME_SCALE), 5, col1=(255, 255, 224))
            window.blit(s, (key_pos(note['note'])*640, 480*2/3 + (note['start'] - pygame.time.get_ticks())/TIME_SCALE))

        for note in hit_list:
            notes_played.remove(note)

        pygame.display.update()
        clock.tick(60)
finally:
    pygame.quit()