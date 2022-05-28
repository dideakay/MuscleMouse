import bitalino
import math
import numpy as np
import time
import pyautogui 

cminX = 0
cmaxX = 0
cminY, cmaxY, cminZ, cmaxZ = 0, 0, 0, 0

def calibrateACCX(runningTime=5, nSamples=1000, channel = -4):
    maxLeftData = np.array([])
    minRightData = np.array([])

    print("Please rotate ACC left for 5 sec...")
    time.sleep(2)
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        maxRawData = device.read(nSamples)
        maxLeftData = np.append(maxLeftData, maxRawData[:,channel])
        end = time.time()

    print("Please rotate ACC right for 5 sec...")
    time.sleep(2)
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        minRawData = device.read(nSamples)
        minRightData= np.append(minRightData, minRawData[:,channel])
        end = time.time()

    minX=np.mean(minRightData)
    maxX=np.mean(maxLeftData)
    print("X min: {}, X max: {}".format(minX, maxX))
    return minX, maxX

def calibrateACCY(runningTime=5, nSamples=1000, channel = -3):
    maxUpData = np.array([])
    minDownData = np.array([])

    print("Please rotate ACC upwards for 5 sec...")
    time.sleep(2)
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        maxRawData = device.read(nSamples)
        maxUpData = np.append(maxUpData, maxRawData[:,channel])
        end = time.time()

    print("Please rotate ACC downwards for 5 sec...")
    time.sleep(2)
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        minRawData = device.read(nSamples)
        minDownData= np.append(minDownData, minRawData[:,channel])
        end = time.time()

    minY=np.mean(minDownData)
    maxY=np.mean(maxUpData)
    return minY, maxY

def calibrateACC(seconds=5):
    minX, maxX = calibrateACCX(seconds)
    minY, maxY = calibrateACCY(seconds)
    return minX, maxX, minY, maxY

#transfers raw EMG input to mV
def transferFunction(ADC, n = 10, VCC = 3.3, Gemg = 1009):
    result = np.array([])
    for data in ADC:
        result = np.append(result, ((((data/math.pow(2, n))-(1/2))*VCC)/Gemg)*1000)
    return result

def rmsValue(array):
    n = len(array)
    squre = 0.0
    root = 0.0
    mean = 0.0
    
    #calculating Squre
    for i in range(0, n):
        squre += (array[i] ** 2)
    #Calculating Mean
    mean = (squre/ (float)(n))
    #Calculating Root
    root = math.sqrt(mean)
    return root

def calibrateEMGRMS(runningTime, nSamples = 1000):
    relaxationData = np.array([])
    contractionData = np.array([])
    # Start Acquisition for Relaxation
    print("Please relax your muscle for calibration for 5 sec...")
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        # Read samples
        relaxationRawData = device.read(nSamples)
        relaxationData = np.append(relaxationData, transferFunction(relaxationRawData[:,-1]))
        end = time.time()
    print ("You may stop now...Prepare to contract ypur muscle in 2 sec...")
    time.sleep(2)
    # Start Acquisition for Contraction
    print("Please contract your muscle for calibration for 5 sec...")
    start = time.time()
    end = time.time()
    while (end - start) < runningTime:
        # Read samples
        contractionRawData = device.read(nSamples)
        contractionData = np.append(contractionData, transferFunction(contractionRawData[:,-1]))
        end = time.time()
    print("rms: ")
    print(rmsValue((contractionData)))
    return rmsValue((contractionData))

macAddress = "20:15:12:22:84:48"
   
device = bitalino.BITalino(macAddress)
time.sleep(1)

srate = 1000
nframes = 100    
device.start(srate, [0,1,2,3]) #0 x, 1 y, 2 z, 3 emg
cminX, cmaxX, cminY, cmaxY = calibrateACC(5)
rmsUpper=calibrateEMGRMS(5)
print ("START")

try:
    while True:

        #EMG
        data = device.read(nframes)
        
        rawDataEMG = data[:, -1]
        transferredData = transferFunction(rawDataEMG)

        rms = rmsValue(transferredData)

        if rms > rmsUpper:
            print(rms)
            pyautogui.click()

        #ACC
        dataX = data[:, -4]
        dataY = data[:,-3]
        meanX=np.mean(dataX)
        meanY = np.mean(dataY)
        
        if (meanX > cmaxX):
            pyautogui.moveRel(xOffset=-5, yOffset=0)

        elif (meanX < cminX): 
            pyautogui.moveRel(xOffset=5, yOffset=0)

        if (meanY > cmaxY):
            pyautogui.moveRel(xOffset=0, yOffset=-5)

        elif (meanY < cminY):
            pyautogui.moveRel(xOffset=0, yOffset=5)

finally:
    print ("STOP")
    device.stop()
    device.close()

