import mido
import pyperclip
from mido import MidiFile
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

def run(midi_file,location_x,location_y,track_number,sfx,volume,pitch,output):
    global f_code
    j = 0
    ticks_per_beat = midi_file.ticks_per_beat
    tempo = None
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    ms_per_beat = tempo / 1000
    ms_per_tick = ms_per_beat / ticks_per_beat

    switch_x = location_x - 1
    switch_y = location_y
    code = (f'Vars.world.tile({location_x},{location_y}).setNet(Blocks.worldProcessor,Team.sharded,0);'
            f'Vars.world.tile({location_x},{location_y}).build.links.add(new LogicBlock.LogicLink({switch_x}, {switch_y}, "switch1", true));'
            f'Vars.world.tile({location_x},{location_y}).build.code="sensor s switch1 @enabled;jump 0 equal s 0;set start @time;')


    f_code = ''
    track = midi_file.tracks[track_number]
    current_time = 0  # Time in ticks
    for msg in track:
        current_time += msg.time
        if msg.type == 'note_on':
            j += 1
            code += (f'j{j}:;op sub time @time start;'
                    f'jump j{j} lessThan time {current_time * ms_per_tick};'
                    f'playsound false {sfx} {volume} {2**((msg.note - pitch) / 12)};')
            if j == 320:
                code += 'control enabled switch1 0";'
                f_code += code
                location_x += 1
                code = (f'Vars.world.tile({location_x},{location_y}).setNet(Blocks.worldProcessor,Team.sharded,0);'
                        f'Vars.world.tile({location_x}, {location_y}).build.links.add(new LogicBlock.LogicLink({switch_x}, {switch_y}, "switch1", true));'
                        f'Vars.world.tile({location_x},{location_y}).build.code="sensor s switch1 @enabled;jump 0 equal s 0;set start @time;')
                j = 0

    code += '"'
    f_code += code
    f_code = f_code + f'; Vars.world.tile({switch_x},{switch_y}).setNet(Blocks.switchBlock,Team.sharded,1)'
    #pyperclip.copy(f_code)
    print("JS code copied to Clipboard!"
          "\nPaste into the game console")

    num_characters = len(f_code)
    print(num_characters)
    truncated_text = f_code[:10000]
    print(truncated_text)
    output.config(state='normal')
    output.insert(tk.END, truncated_text)
    output.config(state='disabled')
    total_characters.config(text=f'total characters : {num_characters}')

def on_button_click():
    midi_file = file.get()
    midi_file = mido.MidiFile(midi_file.replace("\\", "/").replace('"', ''))
    inv = 0

    location_x = file1.get()
    if location_x.isdigit():
        location_x = int(location_x)
        invalid.config(fg='green',text=location_x)
    else:
        invalid.config(fg='red', text='Please enter a number')
        inv = 1

    location_y = file2.get()
    if location_y.isdigit():
        location_y = int(location_y)
        invalid1.config(fg='green', text=location_y)
    else:
        invalid1.config(fg='red', text='Please enter a number')
        inv = 1

    track_number = file3.get()
    if track_number.isdigit():
        track_number = int(track_number)
        invalid2.config(fg='green',text=track_number)
    else:
        invalid2.config(fg='red', text='Please enter a number')
        inv = 1

    sfx = file4.get()
    volume = file5.get()
    if volume.isdigit():
        volume = int(volume)
        invalid3.config(fg='green',text=volume)
    else:
        invalid3.config(fg='red', text='Please enter a number')
        inv = 1

    pitch = file6.get()
    if pitch.isdigit():
        pitch = int(pitch)
        invalid4.config(fg='green',text=pitch)
    else:
        invalid4.config(fg='red', text='Please enter a number')
        inv = 1

    if inv == 1:
        inv = 0
        return

    run(midi_file,location_x,location_y,track_number,sfx,volume,pitch,output)


def copy():
    global f_code
    try:
        pyperclip.copy(f_code)
        copied.config(fg='green', text='Copied!')
    except Exception:
        copied.config(fg='red', text='No Text!')

root = tk.Tk()
root.title("Midi To Mlog")

root.geometry("800x500")
root.resizable(False, False)
root.config(bg='#323740')

invalid = tk.Label(root,text="enter a number", bg='#323740', fg='white', font=(12))
invalid.place(x=175, y=80)
invalid1 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid1.place(x=175, y=110)
invalid2 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid2.place(x=175, y=140)
invalid3 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid3.place(x=175, y=200)
invalid4 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid4.place(x=175, y=230)

tk.Label(root, text="File :",bg='#323740', fg='white',font=(12)).place(x=75, y=50)
tk.Label(root, text="Location X :",bg='#323740', fg='white',font=(12)).place(x=25, y=80)
tk.Label(root, text="Location Y :",bg='#323740', fg='white',font=(12)).place(x=27, y=110)
tk.Label(root, text="Track Number :",bg='#323740', fg='white',font=(12)).place(x=3, y=140)
tk.Label(root, text="Sfx :",bg='#323740', fg='white',font=(12)).place(x=79, y=170)
tk.Label(root, text="Volume :",bg='#323740', fg='white',font=(12)).place(x=47, y=200)
tk.Label(root, text="Pitch :",bg='#323740', fg='white',font=(12)).place(x=65, y=230)
tk.Label(root, text="Output :",bg='#323740', fg='white',font=(12)).place(x=300, y=73)
total_characters = tk.Label(root, text="total characters :",bg='#323740', fg='white',font=(12))
total_characters.place(x=300, y=300)
copied = tk.Label(root, text="asdf",bg='#323740', fg='white',font=(15))
copied.place(x=550, y=330)


file = ttk.Entry(root, style='TEntry', font=(10))
file.place(x=120, y=50, width=300, height=23)
file.insert(0, 'F:/Download (F)/UNDERTALE - ASGORE (Asgores Fight Theme) tracks combined.mid')

file1 = ttk.Entry(root, style='TEntry', font=(10) )
file1.place(x=120, y=80, width=50, height=23)
file1.insert(0, '1')

file2 = ttk.Entry(root, style='TEntry', font=(10) )
file2.place(x=120, y=110, width=50, height=23)
file2.insert(0, '1')

file3 = ttk.Entry(root, style='TEntry', font=(10) )
file3.place(x=120, y=140, width=50, height=23)
file3.insert(0, '0')

file4 = ttk.Entry(root, style='TEntry', font=(10) )
file4.place(x=120, y=170, width=100, height=23)
file4.insert(0, '@sfx-press')

file5 = ttk.Entry(root, style='TEntry', font=(10) )
file5.place(x=120, y=200, width=50, height=23)
file5.insert(0, '1')

file6 = ttk.Entry(root, style='TEntry', font=(10) )
file6.place(x=120, y=230, width=50, height=23)
file6.insert(0, '60')

output = scrolledtext.ScrolledText(root, font=(10), state='disabled')
output.place(x=300, y=95, width=400, height=200)


button = tk.Button(root, text="Generate!", command=on_button_click,font=(13))
button.place(x=60, y=270,width=100,height=50)

copy = tk.Button(root, text="Copy!", command=copy,font=(13))
copy.place(x=550, y=300,width=80,height=30)


root.mainloop()




# @sfx-click
# @sfx-press 60
# @sfx-chatMessage 91
# @sfx-noammo 40
# @sfx-buttonClick 64 not ideal





