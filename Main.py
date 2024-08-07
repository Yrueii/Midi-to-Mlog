import mido
import pyperclip
from mido import MidiFile
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from pymsch import Schematic, Block, Content, ProcessorConfig, ProcessorLink
import base64



def run(midi_file,location_x,location_y,output,speed):
    global f_code
    global sfx_values
    global volume_values
    global pitch_values
    global checked
    
    ticks_per_beat = midi_file.ticks_per_beat
    tempo = None

    total_tracks = len(midi_file.tracks)

    ini_x = location_x
    ini_y = location_y
    switch_x = ini_x - 1
    switch_y = ini_y
    f_code = ''
    
    x = 1
    y = 0
    switchx = 0
    switchy = 0   
    if checked.get() == 1:
        schem = Schematic()
        schem.set_tag('name', 'midi to mlog')
        schem.set_tag('description', file.get())
        schem.add_block(Block(Content.SWITCH, switchx, switchy, None, 0))


    for i in range(total_tracks):
        if i >= 3:
            break

        current_time = 0
        track = midi_file.tracks[i]
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

        sfx = sfx_values[i]
        volume = float(volume_values[i])
        pitch = float(pitch_values[i])
        
        if checked.get() == 1:
            j = 0
            code = 'sensor s switch1 @enabled;jump 0 equal s 0;set start @time;'
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on':
                    j += 1
                    code += (f"""j{j}:;op sub time @time start;
                             jump j{j} lessThan time {(mido.tick2second(current_time, ticks_per_beat, tempo)*1000) / speed};
                             playsound false {sfx} {volume} {2**((msg.note - pitch) / 12)} 0 0 0 false;""")
                    if j == 320:
                        code += 'control enabled switch1 0'
                        schem.add_block(Block(Content.WORLD_PROCESSOR, x, y, ProcessorConfig(code, [ProcessorLink(switchx-x, switchy-y, 'switch1')]).compress(), 0))
                        x += 1
                        if x == 127:
                            x = 0
                            y += 1
                        j = 0
                        code = 'sensor s switch1 @enabled;jump 0 equal s 0;set start @time;'
            code += 'control enabled switch1 0'
            schem.add_block(Block(Content.WORLD_PROCESSOR, x, y, ProcessorConfig(code, [ProcessorLink(switchx-x, switchy-y, 'switch1')]).compress(), 0))
            x = 0
            y += 1

        else:
            j = 0
            code = (f'Vars.world.tile({switch_x},{switch_y}).setNet(Blocks.switchBlock,Team.sharded,1);'
                    f'Vars.world.tile({location_x},{location_y}).setNet(Blocks.worldProcessor,Team.sharded,0);'
                    f'Vars.world.tile({location_x},{location_y}).build.links.add(new LogicBlock.LogicLink({switch_x}, {switch_y}, "switch1", true));'
                    f"Vars.world.build({location_x},{location_y}).updateCode('sensor s switch1 @enabled;jump 0 equal s 0;set start @time;")

            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on':
                    j += 1
                    code += (f'j{j}:;op sub time @time start;'
                            f'jump j{j} lessThan time {(mido.tick2second(current_time, ticks_per_beat, tempo)*1000) / speed};'
                            f'playsound false {sfx} {volume} {2**((msg.note - pitch) / 12)} 0 0 false;')
                    if j == 320:
                        code += "control enabled switch1 0');"
                        f_code += code
                        location_x += 1
                        code = (f'Vars.world.tile({location_x},{location_y}).setNet(Blocks.worldProcessor,Team.sharded,0);'
                                f'Vars.world.tile({location_x}, {location_y}).build.links.add(new LogicBlock.LogicLink({switch_x}, {switch_y}, "switch1", true));'
                                f"Vars.world.build({location_x},{location_y}).updateCode('sensor s switch1 @enabled;jump 0 equal s 0;set start @time;")
                        j = 0
            code += "control enabled switch1 0');"
            f_code += code
            location_x = ini_x
            location_y += 1

    if checked.get() == 1:
        f_code = base64.standard_b64encode(schem.write()).decode()
    #pyperclip.copy(f_code)
    num_characters = len(f_code)
    truncated_text = f_code[:10000]
    output.config(state='normal')
    output.delete(1.0, tk.END)
    output.insert(tk.END, truncated_text)
    output.config(state='disabled')
    total_characters.config(text=f'total characters : {num_characters}')


def on_button_click():
    global track
    global sfx_values
    global volume_values
    global pitch_values
    sfx_values[track] = file4.get()
    volume_values[track] = file5.get()
    pitch_values[track] = file6.get()

    inv = 0
    midi_file = file.get()
    try:
        midi_file = mido.MidiFile(midi_file.replace("\\", "/").replace('"', ''))
        invalidf.config(fg='green', text='valid file location!')
    except Exception:
        invalidf.config(fg='red', text='invalid file location!')
        inv = 1


    if checked.get() == 0:
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
    else:
        location_x = 0
        location_y = 0


    volume_len = len(volume_values)
    inv1 = 0
    for volume_i in range(volume_len):
        try:
            float(volume_values[volume_i])
        except ValueError:
            inv = 1
            inv1 = 1
            while volume_i != (track):
                next_track()
            invalid3.config(fg='red', text='Please enter a number')
            break
    if inv1 == 0:
        invalid3.config(fg='green', text=f'{volume_values[0]}, {volume_values[1]}, {volume_values[2]}')

    pitch_len = len(pitch_values)
    inv2 = 0
    for pitch_i in range(pitch_len):
        try:
            float(pitch_values[pitch_i])
        except ValueError:
            inv = 1
            inv2 = 1
            while pitch_i != (track):
                next_track()
            invalid4.config(fg='red', text='Please enter a number')
            break
    if inv2 == 0:
        invalid4.config(fg='green', text=f'{pitch_values[0]}, {pitch_values[1]}, {pitch_values[2]}')

    speed = file7.get()
    try:
        speed = float(speed)
        invalid5.config(fg='green',text=speed)
    except ValueError:
        invalid5.config(fg='red', text='Please enter a number')
        inv = 1

    if inv == 1:
        inv = 0
        return

    run(midi_file,location_x,location_y,output,speed)


def copy():
    global f_code
    try:
        pyperclip.copy(f_code)
        copied.config(fg='green', text='Copied!')
    except Exception:
        copied.config(fg='red', text='No Text!')

sfx_values = ["Value 1", "@sfx-noammo", "@sfx-click"]
volume_values = ["V1", "0.5", "0.5"]
pitch_values = ["V1", "40", "32"]

def next_track():
    global track
    
    sfx_a = file4.get()
    sfx_values[track] = sfx_a
    volume_a = file5.get()
    volume_values[track] = volume_a
    pitch_a = file6.get()
    pitch_values[track] = pitch_a

    track += 1
    if track >= 3:
        track = 0
    cr_track_num.config(text=f'Track : {track + 1}')

    new_value = sfx_values[track]
    file4.delete(0, tk.END)
    file4.insert(0, new_value)

    new_value = volume_values[track]
    file5.delete(0, tk.END)
    file5.insert(0, new_value)

    new_value = pitch_values[track]
    file6.delete(0, tk.END)
    file6.insert(0, new_value)



root = tk.Tk()
root.title("Midi To Mlog")
track = 0

root.geometry("800x500")
root.resizable(False, False)
root.config(bg='#323740')

invalidf = tk.Label(root,text="", bg='#323740', fg='white', font=(12))
invalidf.place(x=430, y=50)
invalid = tk.Label(root,text="enter a number", bg='#323740', fg='white', font=(12))
invalid.place(x=175, y=80)
invalid1 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid1.place(x=175, y=110)
invalid3 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid3.place(x=185, y=210)
invalid4 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=(12))
invalid4.place(x=185, y=240)
invalid5 = tk.Label(root, text="enter a number", bg='#323740', fg='white', font=('arial', 9))
invalid5.place(x=290, y=130)

tk.Label(root, text="File :",bg='#323740', fg='white',font=(12)).place(x=75, y=50)
tk.Label(root, text="Location X :",bg='#323740', fg='white',font=(12)).place(x=25, y=80)
tk.Label(root, text="Location Y :",bg='#323740', fg='white',font=(12)).place(x=27, y=110)
cr_track_num = tk.Label(root, text="Track : 1",bg='#323740', fg='white',font=('arial', 15))
cr_track_num.place(x=80, y=145)

tk.Label(root, text="Sfx :",bg='#323740', fg='white',font=(12)).place(x=89, y=180)
tk.Label(root, text="Volume :",bg='#323740', fg='white',font=(12)).place(x=57, y=210)
tk.Label(root, text="Pitch :",bg='#323740', fg='white',font=(12)).place(x=75, y=240)
tk.Label(root, text="Speed: ",bg='#323740', fg='white',font=(12)).place(x=300, y=85)

tk.Label(root, text="Output :   (output is truncated, use the copy button to copy)",bg='#323740', fg='white',font=(12)).place(x=380, y=73)
total_characters = tk.Label(root, text="total characters :",bg='#323740', fg='white',font=(12))
total_characters.place(x=380, y=300)
copied = tk.Label(root, text="",bg='#323740', fg='white',font=(15))
copied.place(x=715, y=305)
tk.Label(root, text="File : File location of your midi file, eg",bg='#323740', fg='white',font=(12)).place(x=30, y=330)
tk.Label(root, text="C:/Users/user-name/Downloads/cat.midi",bg='#323740', fg='yellow',font=(12)).place(x=290, y=330)
tk.Label(root, text="Location X : the X coordinates of where you want the processors to be",bg='#323740', fg='white',font=(12)).place(x=30, y=350)
tk.Label(root, text="Location Y : the Y coordinates of where you want the processors to be",bg='#323740', fg='white',font=(12)).place(x=30, y=370)
tk.Label(root, text="Location X and Y is not used for Schematic Mode",bg='#323740', fg='yellow',font=(12)).place(x=50, y=390)
tk.Label(root, text="Track : Some midi files has multiple tracks(the different colored notes you see on a synthesizer app)",bg='#323740', fg='white',font=(12)).place(x=30, y=410)
tk.Label(root, text='you can change the configuration of each track by clicking "Next Track" ',bg='#323740', fg='white',font=(12)).place(x=30, y=430)
tk.Label(root, text="Pitch : the chosen sfx default pitch (60 is c4)",bg='#323740', fg='white',font=(12)).place(x=30, y=450)
tk.Label(root, text="Speed : speed multiplier, 1 is normal, don't put number below 0",bg='#323740', fg='white',font=(12)).place(x=30, y=470)



file = ttk.Entry(root, style='TEntry', font=(10))
file.place(x=120, y=50, width=300, height=23)

file1 = ttk.Entry(root, style='TEntry', font=(10) )
file1.place(x=120, y=80, width=50, height=23)
file1.insert(0, '1')

file2 = ttk.Entry(root, style='TEntry', font=(10) )
file2.place(x=120, y=110, width=50, height=23)
file2.insert(0, '1')

file4 = ttk.Entry(root, style='TEntry', font=(10) )
file4.place(x=130, y=180, width=115, height=23)
file4.insert(0, '@sfx-press')

file5 = ttk.Entry(root, style='TEntry', font=(10) )
file5.place(x=130, y=210, width=50, height=23)
file5.insert(0, '1')

file6 = ttk.Entry(root, style='TEntry', font=(10) )
file6.place(x=130, y=240, width=50, height=23)
file6.insert(0, '60')

file7 = ttk.Entry(root, style='TEntry', font=(10) )
file7.place(x=310, y=110, width=50, height=23)
file7.insert(0, '1')



output = scrolledtext.ScrolledText(root, font=(10), state='disabled')
output.place(x=380, y=95, width=400, height=200)


button = tk.Button(root,bg='lightblue', text="Generate!", command=on_button_click,font=(13))
button.place(x=60, y=270,width=100,height=50)

copy = tk.Button(root,bg='lightblue', text="Copy!", command=copy,font=(13))
copy.place(x=630, y=300,width=80,height=30)

nexttrack = tk.Button(root,bg='lightblue', text="Next Track", command=next_track,font=(13))
nexttrack.place(x=180, y=145,width=80,height=30)

checked = tk.IntVar()
check = ttk.Checkbutton(root, text="Schematic Mode", variable=checked)
check.place(x=580,y=45)

check_style = ttk.Style()
check_style.configure("TCheckbutton",padding=5,font=("Arial", 15),foreground='white',background='#323740')

root.mainloop()


     






