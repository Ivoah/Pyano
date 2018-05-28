#!/usr/bin/env python3

import sys
import mido
import pygame

from pygame.locals import *

from util import *

OCTAVE_RANGE = [5, 6]
WIDTH = 640
HEIGHT = 480

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
#keyb = mido.open_input()
synth = mido.open_output()
clock = pygame.time.Clock()
font = pygame.font.SysFont('Helvetica', 12)

midi_file = mido.MidiFile(sys.argv[1])
song = []
pending_notes = {}
cur_time = 0

for msg in midi_file:
    cur_time += msg.time
    if msg.type == 'note_on' and msg.velocity > 0:
        pending_notes[(msg.channel, msg.note)] = [cur_time, msg.velocity]
        OCTAVE_RANGE[0] = min(OCTAVE_RANGE[0], msg.note//12)
        OCTAVE_RANGE[1] = max(OCTAVE_RANGE[1], msg.note//12 + 1)
    elif msg.type == 'note_off' or msg.type == 'note_on' and msg.velocity == 0:
        song.append({
            'note': msg.note,
            'channel': msg.channel,
            'velocity': pending_notes[(msg.channel, msg.note)][1],
            'start': pending_notes[(msg.channel, msg.note)][0]*1000,
            'stop': cur_time*1000,
            'status': 'unplayed'
        })

song = sorted(song, key=lambda note: note['start'])

notes_played = []

try:
    running = True
    while running:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.mod == 1024 and event.key == 113) or event.type == QUIT:
                running = False

        msg = None #keyb.poll()
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

        highlight = {}
        for note in song:
            if note_visible(note, pygame.time.get_ticks(), HEIGHT*2/3):
                s = border_box((key_width(note['note'])*WIDTH/(OCTAVE_RANGE[1] - OCTAVE_RANGE[0]), (note['stop'] - note['start'])/TIME_SCALE), 3, col1=channel_colors[note['channel']])
                pos = (((note['note']//12 - OCTAVE_RANGE[0]) + key_pos(note['note']))*WIDTH/(OCTAVE_RANGE[1] - OCTAVE_RANGE[0]), HEIGHT*2/3 - (note['stop'] - pygame.time.get_ticks())/TIME_SCALE)
                window.blit(s, pos)

            if note['start'] <= pygame.time.get_ticks() and note['status'] == 'unplayed':
                note['status'] = 'playing'
                synth.send(mido.Message('note_on', note=note['note'], channel=note['channel'], velocity=note['velocity']))
            elif note['stop'] <= pygame.time.get_ticks() and note['status'] == 'playing':
                note['status'] = 'played'
                synth.send(mido.Message('note_off', note=note['note'], channel=note['channel']))

            if note['status'] == 'playing':
                highlight[note['note']] = note['channel']

        window.blit(draw_octaves((WIDTH, HEIGHT/3), OCTAVE_RANGE, highlight), (0, HEIGHT*2/3))

        window.blit(font.render(str(clock.get_fps()), True, (0, 0, 0)), (10, 10))

        pygame.display.flip()
        clock.tick(60)
finally:
    pygame.quit()