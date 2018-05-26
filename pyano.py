#!/usr/bin/env python3

import mido
import pygame
import pygame.time

from pygame.locals import *

from util import *

TIME_SCALE = 5

channel_colors = [
    ((0x5a, 0x9f, 0xd4), (0x30, 0x69, 0x98)),
    ((0xff, 0xd4, 0x3b), (0xff, 0xe8, 0x73))
]

pygame.init()

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
                    'note': msg.note,
                    'channel': msg.channel,
                    'start': pygame.time.get_ticks(),
                    'stop': None
                })
            elif msg.type == 'note_off' or msg.type == 'note_on' and msg.velocity == 0:
                for note in notes_played:
                    if note['note'] == msg.note and note['stop'] is None:
                        note['stop'] = pygame.time.get_ticks()

        window.fill((0, 255, 255))
        window.blit(draw_octave((640, 480/3), 5, [note['note'] for note in notes_played if note['stop'] is None]), (0, 480*2/3))

        hit_list = []
        for note in sorted(notes_played, key=lambda n: n['start']):
            if note['stop'] is not None and note['stop'] < (pygame.time.get_ticks() - (480*2/3)*TIME_SCALE): hit_list.append(note)
            s = border_box((key_width(note['note'])*640, ((note['stop'] or pygame.time.get_ticks()) - note['start'])/TIME_SCALE), 5, col1=channel_colors[note['channel']])
            window.blit(s, (key_pos(note['note'])*640, 480*2/3 + (note['start'] - pygame.time.get_ticks())/TIME_SCALE))

        for note in hit_list:
            notes_played.remove(note)

        pygame.display.update()
        clock.tick(60)
finally:
    pygame.quit()