#! /usr/bin/env python
######################################################################
# tuner.py - a minimal command-line guitar/ukulele tuner in Python.
# Requires numpy and pyaudio.
######################################################################
# Author:  Matt Zucker
# Date:	July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#		  https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################

import numpy as np
import pyaudio


NOTE_MIN = 60	   # C4
NOTE_MAX = 70	   # A5
FSAMP = 48000	   # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n//12 - 1)
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP

class Tuner:
	def __init__(self):
		self.imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
		self.imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

		self.buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)

		pa = pyaudio.PyAudio()
		#for i in range(p.get_device_count()):
			#dev = p.get_device_info_by_index(i)
			#print((i,dev['name'],dev['maxInputChannels']))
			#print(dev)
		self.stream = pa.open(format=pyaudio.paInt16,
										channels=1,
										rate=FSAMP,
										input=True,
										frames_per_buffer=FRAME_SIZE,
										input_device_index=1)

		print('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')

		self.n0_last = [0,0]
	
	def start(self):
		self.stream.start_stream()

	def stop(self):
		self.stream.stop_stream()


	def find_pitch(self,):
		# Run the FFT on the windowed buffer
		window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))
		fft = np.fft.rfft(self.buf * window)

		# Get frequency of maximum response in range
		freq = (np.abs(fft[self.imin:self.imax]).argmax() + self.imin) * FREQ_STEP
		amp = np.abs(fft[self.imin:self.imax]).max()

		# Get note number and nearest note
		n = freq_to_number(freq)
		n0 = int(round(n))

		ret = None
		th = freq**2*8
		th = freq*2e3
		if n0 == self.n0_last[1] and n0 != self.n0_last[0] and amp > th:
			ret = n0
		if n0 != self.n0_last[1] or amp > th:
			self.n0_last[0] = self.n0_last[1]
			self.n0_last[1] = n0
#if amp > freq*2e3:
#if ret != None: print('freq: {:7.2f} Hz	 note: {:>3s} {:+.2f} amp: {}k'.format(freq, note_name(n0), n-n0, round(amp/1e3)),self.n0_last)
		return ret 

	def next_buf(self):
		self.buf[:-FRAME_SIZE] = self.buf[FRAME_SIZE:]
		self.buf[-FRAME_SIZE:] = np.fromstring(self.stream.read(FRAME_SIZE), np.int16)


if __name__=='__main__':
	tuner = Tuner()
	while tuner.stream.is_active():
		
		tuner.next_buf()
		n0 = tuner.find_pitch()
		if n0: print(note_name(n0))


