# << Oscilloscope GUI >>
#
# This implementaion makes use of matplotlib on Tk for agile GUI development.
#
# Reference: https://matplotlib.org/2.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
#

import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import tkinter as Tk
import dsp
from datetime import datetime
import time
import os

import matplotlib.pyplot as plt
plt.style.use('dark_background')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("port", help="serial port identifier")
parser.add_argument("-d", "--debug", help="serial port identifier", action="store_true")
args = parser.parse_args()

mode = dsp.ENDFIRE

if __name__ == '__main__':

    gui = dsp.GUI(port = args.port)

    ### Default settings to DSP ###
    gui.set_beam_forming(mode, 'c')  # ENDFIRE mode, center
    gui.enable_pre_emphasis(True)  # Pre emphasis enabled
    ###############################

    matplotlib.use('TkAgg')

    PADX = 6
    PADX_GRID = 2
    PADY_GRID = 2

    CMAP_LIST = ('hot',
                 'viridis',
                 'gray',
                 'binary',
                 'ocean',
                 'magma',
                 'cubehelix',
                 'cool',
                 'winter',
                 'summer')

    ANGLE = ('L', 'l', 'c', 'r', 'R')

    root = Tk.Tk()
    root.wm_title("Oscilloscope")

    fig = Figure(figsize=(11, 4), dpi=100)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.15)

    frame = Tk.Frame(master=root)
    frame_row0 = Tk.Frame(master=frame)
    frame_row1 = Tk.Frame(master=frame)
    frame_row2 = Tk.Frame(master=frame)
    frame_row3 = Tk.Frame(master=frame)

    canvas = FigureCanvasTkAgg(fig, master=frame_row0)
    canvas.show()

    ### Row 1 ####
    entry = Tk.Entry(master=frame_row1, width=14)
    #cmap = Tk.Spinbox(master=frame_row1, width=10, values=CMAP_LIST)
    var_cmap = Tk.StringVar()
    var_cmap.set('hot')
    cmap = Tk.OptionMenu(frame_row1, var_cmap, *CMAP_LIST)
    counter = Tk.Label(master=frame_row1)
    range_amplitude = Tk.Spinbox(master=frame_row1, width=6, values=[2**8, 2**9, 2**11, 2**13, 2**15])
    range_mel_spectrogram = Tk.Spinbox(master=frame_row1, width=3, values=[dsp.NUM_FILTERS, int(dsp.NUM_FILTERS*.8), int(dsp.NUM_FILTERS*0.6)])
    range_spectrogram = Tk.Spinbox(master=frame_row1, width=4, values=[int(dsp.NN/2), int(dsp.NN/2.0*.7), int(dsp.NN/2.0*0.4)])
    range_mfcc = Tk.Spinbox(master=frame_row1, width=3, values=[25, 18, 13])
    spectrum_subtraction = Tk.Spinbox(master=frame_row1, width=3, values=[0, 10, 15, 20, 25])

    ### Row 2 ####
    cnt = 0
    class_label_ = ''
    counter.configure(text='({})'.format(str(0)))
    repeat_action = False
    filename = None

    # Save training data for deep learning
    def save_training_data(mag, step):
        global class_label_, cnt, filename
        class_label = entry.get()
        dt = datetime.today().strftime('%Y%m%d%H%M%S')
        if class_label == '':
            filename = './data/{}-{}'.format(step, dt)
        else:
            filename = './data/{}-{}-{}'.format(entry.get(), step, dt)
            with open(filename+'.csv', "w") as f:
                f.write(','.join(mag.astype(str)))
            if class_label_ != class_label:
                class_label_ = class_label
                cnt = 0
            cnt += 1
            counter.configure(text='({})'.format(str(cnt)))

    # Repeat an operation
    def repeat(func):
        if repeat_action:
            root.after(50, func)

    def raw_wave():
        range_ = int(range_amplitude.get())
        ax.grid(True, alpha=0.3)
        mag = gui.plot_aed(ax, dsp.RAW_WAVE, range_=range_)
        fig.tight_layout()
        canvas.draw()
        save_training_data(mag, 'waveform')
        repeat(raw_wave)

    def fft():
        ssub = int(spectrum_subtraction.get())
        ax.grid(True, alpha=0.3)
        mag = gui.plot_aed(ax, dsp.FFT, ssub=ssub)
        fig.tight_layout()
        canvas.draw()
        save_training_data(mag, 'fft')
        repeat(fft)

    def spectrogram():
        ssub = int(spectrum_subtraction.get())    
        range_ = int(range_spectrogram.get())
        cmap_ = var_cmap.get()
        mag = gui.plot_aed(ax, dsp.SPECTROGRAM, range_, cmap_, ssub)
        fig.tight_layout()
        canvas.draw()
        save_training_data(mag, 'spectrogram')
        repeat(spectrogram)

    def mel_spectrogram():
        ssub = int(spectrum_subtraction.get())
        range_ = int(range_mel_spectrogram.get())
        cmap_ = var_cmap.get()
        mag = gui.plot_aed(ax, dsp.MEL_SPECTROGRAM, range_, cmap_, ssub)
        fig.tight_layout()
        canvas.draw()
        save_training_data(mag, 'mel_spectrogram')
        repeat(mel_spectrogram)

    def mfcc():
        ssub = int(spectrum_subtraction.get())    
        range_ = int(range_mfcc.get())
        cmap_ = var_cmap.get()
        mag = gui.plot_aed(ax, dsp.MFCC, range_, cmap_, ssub)
        fig.tight_layout()
        canvas.draw()
        save_training_data(mag, 'mfcc')
        repeat(mfcc)

    def beam_forming(angle):
        global mode
        angle = int(angle) + 2
        gui.set_beam_forming(mode, ANGLE[angle])

    def repeat_toggle():
        global repeat_action
        if repeat_action == True:
            repeat_action = False
            button_repeat.configure(bg='lightblue')
        else:
            repeat_action = True
            button_repeat.configure(bg='red')
            
    def pre_emphasis_toggle():
        if button_pre_emphasis.cget('bg') == 'lightblue':
            button_pre_emphasis.configure(bg='red')
            gui.enable_pre_emphasis(True)
        else:       
            button_pre_emphasis.configure(bg='lightblue')
            gui.enable_pre_emphasis(False)
            
    def savefig():
        global filename
        if filename:
            fig.savefig(filename+'.png')

    def remove():
        global filename, cnt
        if filename:
            os.remove(filename+'.csv')
            cnt -= 1
            counter.configure(text='({})'.format(str(cnt)))

    def _quit():
        root.quit()
        root.destroy()

    def filterbank():
        mag = gui.plot_aed(ax, dsp.FILTERBANK)
        canvas.draw()

    def elapsed_time():
        gui.plot_aed(ax, dsp.ELAPSED_TIME)

    def broadside():
        global mode
        mode = dsp.BROADSIDE
        angle = range_beam_forming.get() + 2
        gui.set_beam_forming(mode, ANGLE[angle])

    def endfire():
        global mode
        mode = dsp.ENDFIRE
        angle = int(range_beam_forming.get()) + 2
        gui.set_beam_forming(mode, ANGLE[angle])

    def left_mic_only():
        gui.left_mic_only()

    def right_mic_only():
        gui.right_mic_only()

    ### Row 1 ####

    label_class = Tk.Label(master=frame_row1, text='Class label:')
    label_image = Tk.Label(master=frame_row1, text='Subtraction:')
    label_color = Tk.Label(master=frame_row1, text='Color:')
    button_waveform = Tk.Button(master=frame_row1, text='Wave', command=raw_wave, bg='lightblue', activebackground='grey', padx=PADX)
    button_psd = Tk.Button(master=frame_row1, text='FFT', command=fft, bg='lightblue', activebackground='grey', padx=PADX)
    button_spectrogram = Tk.Button(master=frame_row1, text='Spec', command=spectrogram, bg='lightblue', activebackground='grey', padx=PADX)
    button_mel_spectrogram = Tk.Button(master=frame_row1, text='Mel spec', command=mel_spectrogram, bg='pink', activebackground='grey', padx=PADX)
    button_mfcc = Tk.Button(master=frame_row1, text='MFCCs', command=mfcc, bg='yellowgreen', activebackground='grey', padx=PADX)

    ### Row 2 ####

    button_repeat = Tk.Button(master=frame_row2, text='Repeat', command=repeat_toggle, bg='lightblue', activebackground='grey', padx=PADX)
    button_pre_emphasis = Tk.Button(master=frame_row2, text='Emphasis', command=pre_emphasis_toggle, bg='red', activebackground='grey', padx=PADX)
    button_savefig = Tk.Button(master=frame_row2, text='Savefig', command=savefig, bg='lightblue', activebackground='grey', padx=PADX)
    button_remove = Tk.Button(master=frame_row2, text='Remove', command=remove, bg='lightblue', activebackground='grey', padx=PADX)
    button_quit = Tk.Button(master=frame_row2, text='Quit', command=_quit, bg='yellow', activebackground='grey', padx=PADX)

    label_beam_forming = Tk.Label(master=frame_row2, text='Beam forming:')
    label_left = Tk.Label(master=frame_row2, text='L')
    label_right = Tk.Label(master=frame_row2, text='R')
    range_beam_forming = Tk.Scale(master=frame_row2, orient=Tk.HORIZONTAL, length=70, from_=-1, to=1, showvalue=0, command=beam_forming)

    ### Row 3 ####
    
    button_filterbank = Tk.Button(master=frame_row3, text='Filterbank', command=filterbank, bg='lightblue', activebackground='grey', padx=PADX)
    button_elapsed_time = Tk.Button(master=frame_row3, text='Elapsed time', command=elapsed_time, bg='lightblue', activebackground='grey', padx=PADX)
    button_broadside = Tk.Button(master=frame_row3, text='Broadside', command=broadside, bg='lightblue', activebackground='grey', padx=PADX)
    button_endfire = Tk.Button(master=frame_row3, text='Endfire', command=endfire, bg='lightblue', activebackground='grey', padx=PADX)
    button_left_mic_only = Tk.Button(master=frame_row3, text='Left mic only', command=left_mic_only, bg='lightblue', activebackground='grey', padx=PADX)
    button_right_mic_only = Tk.Button(master=frame_row3, text='Right mic only', command=right_mic_only, bg='lightblue', activebackground='grey', padx=PADX)

    ##### Place the parts on Tk #####

    frame.pack(expand=True, fill=Tk.BOTH)

    ### Row 0: main canvas
    frame_row0.pack(expand=True, fill=Tk.BOTH)
    canvas._tkcanvas.pack(expand=True, fill=Tk.BOTH)

    ### Row 1: operation ####

    frame_row1.pack(pady=PADY_GRID)

    # Class label entry
    label_class.grid(row=0, column=0, padx=PADX_GRID)
    entry.grid(row=0, column=1, padx=PADX_GRID)
    counter.grid(row=0, column=2, padx=PADX_GRID)

    # Waveform
    range_amplitude.grid(row=0, column=3, padx=PADX_GRID)
    button_waveform.grid(row=0, column=4, padx=PADX_GRID)

    # FFT (PSD)
    button_psd.grid(row=0, column=5, padx=PADX_GRID)

    # Linear-scale Spectrogram (PSD)
    range_spectrogram.grid(row=0, column=6, padx=PADX_GRID)
    button_spectrogram.grid(row=0, column=7, padx=PADX_GRID)

    # Mel-scale Spectrogram (PSD)
    range_mel_spectrogram.grid(row=0, column=8, padx=PADX_GRID)
    button_mel_spectrogram.grid(row=0, column=9, padx=PADX_GRID)

    # MFCC
    range_mfcc.grid(row=0, column=10, padx=PADX_GRID)
    button_mfcc.grid(row=0, column=11, padx=PADX_GRID)

    # CMAP
    label_image.grid(row=0, column=12, padx=PADX_GRID)
    label_image.grid(row=0, column=13, padx=PADX_GRID)
    spectrum_subtraction.grid(row=0, column=14, padx=PADX_GRID)
    cmap.grid(row=0, column=15, padx=PADX_GRID)

    ### Row 2 ####

    frame_row2.pack(pady=PADY_GRID)

    # Beam forming
    label_beam_forming.grid(row=0, column=0, padx=PADX_GRID)
    label_left.grid(row=0, column=1, padx=PADX_GRID)
    range_beam_forming.grid(row=0, column=2, padx=PADX_GRID)
    label_right.grid(row=0, column=3, padx=PADX_GRID)

    # Repeat, pre_emphasis, save fig and delete
    button_repeat.grid(row=0, column=4, padx=PADX_GRID)
    button_pre_emphasis.grid(row=0, column=5, padx=PADX_GRID)
    button_savefig.grid(row=0, column=6, padx=PADX_GRID)
    button_remove.grid(row=0, column=7, padx=PADX_GRID)
        
    # Quit
    button_quit.grid(row=0, column=9, padx=PADX_GRID)

    ### Row 3 ####

    # DEBUG
    if args.debug:
        frame_row3.pack(pady=PADY_GRID)
        button_filterbank.grid(row=0, column=0, padx=PADX_GRID)
        button_elapsed_time.grid(row=0, column=1, padx=PADX_GRID)
        button_broadside.grid(row=0, column=2, padx=PADX_GRID)    
        button_endfire.grid(row=0, column=3, padx=PADX_GRID)            
        button_left_mic_only.grid(row=0, column=4, padx=PADX_GRID)    
        button_right_mic_only.grid(row=0, column=5, padx=PADX_GRID)    

    ##### loop forever #####
    Tk.mainloop()
