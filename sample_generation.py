from math import *
import os
from scipy.io.wavfile import write
from scipy.ndimage import uniform_filter1d
from scipy.signal import welch
import matplotlib.pyplot as plt
import numpy as np
import time

print("started...")

# create float[] full of data points from text file outputted by yade
sampleData = np.genfromtxt('./data.txt',dtype=None,names=True)
data1 = sampleData['surfacevelocityabovethreshw1']
data2 = sampleData['surfacevelocityabovethreshw2']
data3 = sampleData['surfacevelocityabovethreshw3']
data4 = sampleData['surfacevelocityw1']
data5 = sampleData['surfacevelocityw2']
data6 = sampleData['surfacevelocityw3']
t = sampleData['t']
# magic number is taken from the calculated PWaveTimeStep() in YADE
dataTimeLength = 1.1510864433221335e-06 * len(t)
tsecondsSR = [dataTimeLength/(i + 1) for i in range(len(t))]
print("retrieved data...")
print(f"data will create {dataTimeLength} seconds of audio.")

# create paths for each audio file
savePath1 = "."
savePath2 = "."
savePath3 = "."
savePath4 = "."
savePath5 = "."
savePath6 = "."
print("created audio paths...")


# normalize all data
normalizedData1 = ((data1 - data1.min()) / (data1.max() - data1.min()) )
normalizedData2 = ((data2 - data2.min()) / (data2.max() - data2.min()) )
normalizedData3 = ((data3 - data3.min()) / (data3.max() - data3.min()) )
normalizedData4 = ((data4 - data4.min()) / (data4.max() - data4.min()) )
normalizedData5 = ((data5 - data5.min()) / (data5.max() - data5.min()) )
normalizedData6 = ((data6 - data6.min()) / (data6.max() - data6.min()) )
print("normalized data...")

sampleRate = 44100
# sample dataset at sampleRate Hz
def getDataAtSR(array):
    sampledArray = []
    interval = len(array) / (sampleRate * dataTimeLength)
    for i in range(sampleRate):
        sampledArray.append(array[int(i * interval)])
    return np.array(sampledArray, dtype=float)

# take the moving average of each dataset
movingAverageData1 = uniform_filter1d(getDataAtSR(normalizedData1), size=630)
movingAverageData2 = uniform_filter1d(getDataAtSR(normalizedData2), size=630)
movingAverageData3 = uniform_filter1d(getDataAtSR(normalizedData3), size=630)
movingAverageData4 = uniform_filter1d(getDataAtSR(normalizedData4), size=630)
movingAverageData5 = uniform_filter1d(getDataAtSR(normalizedData5), size=630)
movingAverageData6 = uniform_filter1d(getDataAtSR(normalizedData6), size=630)
print("calculated moving averages...")

# subtract moving average data from original data
finalData1 = getDataAtSR(normalizedData1) - movingAverageData1
finalData2 = getDataAtSR(normalizedData2) - movingAverageData2
finalData3 = getDataAtSR(normalizedData3) - movingAverageData3
finalData4 = getDataAtSR(normalizedData4) - movingAverageData4
finalData5 = getDataAtSR(normalizedData5) - movingAverageData5
finalData6 = getDataAtSR(normalizedData6) - movingAverageData6
print("subtracted moving averages from original data...")

# plot it
fig, axs = plt.subplots(3,2)
axs[0,0].plot(range(len(finalData1)),finalData1)
axs[0,0].set_title('data1')
print("plotted data 1...")
axs[1,0].plot(range(len(finalData2)),finalData2)
axs[1,0].set_title('data2')
print("plotted data 2...")
axs[2,0].plot(range(len(finalData3)),finalData3)
axs[2,0].set_title('data3')
print("plotted data 3...")
axs[0,1].plot(range(len(finalData4)),finalData4)
axs[0,1].set_title('data4')
print("plotted data 4...")
axs[1,1].plot(range(len(finalData5)),finalData5)
axs[1,1].set_title('data5')
print("plotted data 5...")
axs[2,1].plot(range(len(finalData6)),finalData6)
axs[2,1].set_title('data6')
print("plotted data 6...")
plt.legend()
plt.xlabel('time (seconds)')
plt.ylabel('magnitude')
print("done plotting! exit the plot to write to an audio file")
plt.show()

print("writing to files...")
# save the file!
write(savePath1, sampleRate, finalData1)
write(savePath2, sampleRate, finalData2)
write(savePath3, sampleRate, finalData3)
write(savePath4, sampleRate, finalData4)
write(savePath5, sampleRate, finalData5)
write(savePath6, sampleRate, finalData6)
print("files written, process completed successfully.")
