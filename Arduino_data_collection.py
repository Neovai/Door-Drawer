import serial
import time
import csv

ser = serial.Serial('COM4') #change com port for arduino
ser.flushInput()
data = []

timer = time.perf_counter() + 8; #runs for 8 seconds

while timer > time.perf_counter():
    ser_bytes = ser.readline()
    decoded_bytes = float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
    data.append([decoded_bytes])
    print(decoded_bytes)
   # with open("data.csv","a") as f: #"a" stands for appending data to same csv file
    #    writer = csv.writer(f,delimiter=",")
     #   writer.writerow([decoded_bytes])
for i in range(0,len(data)):
    with open("test_data.csv","a") as f: 
        writer = csv.writer(f,delimiter=",")
        writer.writerow(data[i])
