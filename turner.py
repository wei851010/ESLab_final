from time import sleep
import serial

def flip():
	ser.write(b'a')
	sleep(3)

if __name__=='__main__':
	ser = serial.Serial('/dev/ttyUSB0', 9600)
	ser.write(b'a')
