import mido

midi = mido.MidiFile('Still Alive.mid')

for note in midi.tracks[2]:
    print(note)