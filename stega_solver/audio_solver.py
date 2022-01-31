# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:18:08 2021
"""  
try:
    import wave
    import pylab
    from datetime import datetime
    from scipy.io import wavfile as wav
    import numpy as np
except Exception as e:
    raise ImportError("audio_solver.py -> " + str(e))


"SPECTROGRAME WAV"
def graph_spectrogram(challenge,wav_file):
    sound_info, frame_rate = get_wav_info(str(wav_file))
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % wav_file)
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig(challenge.directory+"/spectrogram"+str(datetime.now().hour)+"."+str(datetime.now().minute)+"."+str(datetime.now().second)+".png")
    print("Spectrogram saved in stega_solver")
    
def get_wav_info(challenge,wav_file):
    wav = wave.open(str(wav_file), 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate




def isNumberInArray(array, number):
    offset = 100
    for i in range(number - offset, number + offset):
        if i in array:
                return True
    return False

def dtmf(challenge,file):
    DTMF_TABLE = {
    '1': [1209, 697],
    '2': [1336, 697],
    '3': [1477, 697],
    'A': [1633, 697],

    '4': [1209, 770],
    '5': [1336, 770],
    '6': [1477, 770],
    'B': [1633, 770],

    '7': [1209, 852],
    '8': [1336, 852],
    '9': [1477, 852],
    'C': [1633, 852],

    '*': [1209, 941],
    '0': [1336, 941],
    '#': [1477, 941],
    'D': [1633, 941],
    } 
    rate, data = wav.read(str(file))

    # Calculate fourier trasform of data
    FourierTransformOfData = np.fft.fft(data, 20000)
    # Convert fourier transform complex number to integer numbers
    for i in range(len(FourierTransformOfData)):
        FourierTransformOfData[i] = int(np.absolute(FourierTransformOfData[i]))
    # Calculate lower bound for filtering fourier trasform numbers
    LowerBound = 1* np.average(FourierTransformOfData)
    # Filter fourier transform data (only select frequencies that X(jw) is greater than LowerBound)
    FilteredFrequencies = []
    for i in range(len(FourierTransformOfData)):
        if (FourierTransformOfData[i] > LowerBound):
                FilteredFrequencies.append(i)
    # Detect and print pressed button

    flag=""
    for char, frequency_pair in DTMF_TABLE.items():
        if (isNumberInArray(FilteredFrequencies, frequency_pair[0]) and
            isNumberInArray(FilteredFrequencies, frequency_pair[1])):
                flag+=char

    if flag != "":
        challenge.log("Stega dtmf flag:",flag)
    else:
        challenge.log("Stega, no dtmf")
