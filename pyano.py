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

pygame.display.set_caption('Pyano')
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
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
playback_time = 0
playing = True

try:
    running = True
    while running:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.mod == 1024 and event.key == 113) or event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                playing = not playing

        playback_time += clock.get_time() if playing else 0

        window.fill((0, 255, 255))

        highlight = {}
        for note in song:
            if note_visible(note, playback_time, HEIGHT*2/3):
                s = border_box((key_width(note['note'])*WIDTH/(OCTAVE_RANGE[1] - OCTAVE_RANGE[0]), (note['stop'] - note['start'])/TIME_SCALE), 3, col1=channel_colors[note['channel']])
                pos = (((note['note']//12 - OCTAVE_RANGE[0]) + key_pos(note['note']))*WIDTH/(OCTAVE_RANGE[1] - OCTAVE_RANGE[0]), HEIGHT*2/3 - (note['stop'] - playback_time)/TIME_SCALE)
                window.blit(s, pos)

            if note['start'] <= playback_time and note['status'] == 'unplayed':
                note['status'] = 'playing'
                synth.send(mido.Message('note_on', note=note['note'], channel=note['channel'], velocity=note['velocity']))
            elif note['stop'] <= playback_time and note['status'] == 'playing':
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