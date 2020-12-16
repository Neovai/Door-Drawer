import serial
import time
import csv

ser = serial.Serial('COM10') #change com port for arduino
ser.flushInput()
data = []

while True:
    try:
        #print("running...")
        ser_bytes = ser.readline()
        decoded_bytes = float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        data.append([decoded_bytes])
        print(decoded_bytes) #for testing purposes
        #with open("test_data.csv","a") as f: #"a" stands for appending data to same csv file
         #   writer = csv.writer(f,delimiter=",")
          #  writer.writerow([decoded_bytes])
    except:
        print("keyboard Interrupt") #press ctrl-c to break the loop
        break
    for i in len(data):
        with open("test_data.csv","a") as f: #"a" stands for appending data to same csv file
            writer = csv.writer(f,delimiter=",")
            writer.writerow([decoded_bytes])

