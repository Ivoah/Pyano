#!/usr/bin/env python3

import mido
import pygame

from pygame.locals import *

from util import *

OCTAVE_RANGE = [3, 4, 5]
WIDTH = 640
HEIGHT = 480

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
keyb = mido.open_input()
synth = mido.open_output()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Helvetica', 12)

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

        hit_list = []
        for note in sorted(notes_played, key=lambda n: n['start']):
            if note['stop'] is not None and note['stop'] < (pygame.time.get_ticks() - (HEIGHT*2/3)*TIME_SCALE): hit_list.append(note)
            s = border_box((key_width(note['note'])*WIDTH, ((note['stop'] or pygame.time.get_ticks()) - note['start'])/TIME_SCALE), 5, col1=channel_colors[note['channel']])
            window.blit(s, (key_pos(note['note'])*WIDTH, HEIGHT*2/3 + (note['start'] - pygame.time.get_ticks())/TIME_SCALE))

        for note in hit_list:
            notes_played.remove(note)

        for note in song:
            if note_visible(note, pygame.time.get_ticks(), HEIGHT*2/3):
                window.blit(*draw_note(note, pygame.time.get_ticks(), WIDTH, HEIGHT*2/3))

        for octave in OCTAVE_RANGE:
            window.blit(draw_octave((WIDTH/len(OCTAVE_RANGE), HEIGHT/3), octave, [note['note'] for note in notes_played if note['stop'] is None]), ((octave - OCTAVE_RANGE[0])*WIDTH/len(OCTAVE_RANGE), HEIGHT*2/3))

        window.blit(font.render(str(clock.get_fps()), True, (0, 0, 0)), (10, 10))

        pygame.display.flip()
        clock.tick(60)
finally:
    pygame.quit()