from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import serial
from time import sleep

from tuner import * 
from reader import *
#from turner import *

ser = serial.Serial('/dev/ttyUSB0', 9600)


camera = PiCamera()
camera.contrast = 100
camera.saturation = -100
camera.brightness = 70
camera.ISO = 100
camera.sharpness = 50
camera.resolution = (2592, 1944)

reader = Reader()


def flip():
	ser.write(b'a')
	sleep(3)

def get_frame():
	rawCapture = PiRGBArray(camera,size=(2592,1944))
	camera.capture(rawCapture, format="bgr")
	image = rawCapture.array
	return image

def main():
	'''
	camera.start_preview()
	sleep(9)
	camera.stop_preview()
	'''
	state = 'cam'
	tuner = Tuner()
	while True:
		if state == 'cam':
			print('cam')
			img = get_frame()
			state = 'read'

		elif state == 'read':
			print('read')
			img = cv2.imread('./phone_1.png')
			pitch = reader.read(img)[:-3]
			print(pitch)

			state = 'listen'
			
		elif state == 'listen':
			print('listen')
			compare_idx = 0
			tuner.start()
			while True:
				try:
					tuner.next_buf() #needed to updata data
					n0 = tuner.find_pitch()
					if n0: print(note_name(n0))
					if n0 and pitch[compare_idx]==note_name(n0)[0]:
						compare_idx += 1
						if compare_idx==len(pitch): break
					elif n0:
						compare_idx = 0
				except:
					print('Input Overflow')
					del tuner
					tuner = Tuner()
					tuner.start()
			
			tuner.stop()
			state = 'flip'

		elif state == 'flip':
			print('flip')
			flip()
			state = 'cam'

if __name__=='__main__':
	main()

