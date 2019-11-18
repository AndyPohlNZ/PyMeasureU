#!/usr/bin/python3

from imeasureu import IMeasureU
import warnings
import matplotlib.pyplot as plt


class Session():
    '''
    Class to process a data collection session ultising multiple IMeasureU Sensors

    Created by: Andy Pohl - andrew.pohl@ucalgary.ca
                University of Calgary
                November 2019
    '''
    def __init__(self, name, numSensors):
        self.name = name
        self.numSensors = numSensors
        self.sensorData = []

    def loadSensorData(self, resample=False, desiredSampleRate=200):
        '''
        Loads individual sensorData into the Session object

        Args:
            resample <bool>: Should the raw sensor data be resampled
            desiredSampleRate <int>: If raw data is being resampled, to what rate.

        Returns: 
            void
        '''

        # Load Sensor Data
        print("Loading Sensor Data")
        sensor_count = 0
        while sensor_count < self.numSensors:
            fileloc = input("Provide location of sensor %.0f:" % (sensor_count +1))
            name = input("Specify name of sensor %.0f:" % (sensor_count +1))
            print("Loading Sensor %.0f"% (sensor_count+1))

            sensor = IMeasureU(fileloc, name)
            sensor.loadData()
            if resample:
                sensor.resample(desiredSampleRate)

            
            self.sensorData.append(sensor)
            
            sensor_count +=1

        # Check if sensor recordings are the same length (they should be if synchronsied)
        sensor_lengths = []
        for i in range(len(self.sensorData)):
            sensor_lengths.append(self.sensorData[i].recordTime)


        if not checkEqual(sensor_lengths):
            warnings.warn("Not all sensor data provided recorded for the same length.  Are you sure the all sensors are from the same session?", Warning)

    def trim(self):

        # make subplot

        sensor_names = [sensor.name for sensor in self.sensorData]
        sensor_idx = None
        while sensor_idx is None:
            try:
                trim_sensor = input("Specify name of sensor to identify trim points:")
                sensor_idx = sensor_names.index(trim_sensor)
                break
            except ValueError:
                print("%s is not the name of a sensor in your session. Please try again." % (trim_sensor))

        
        sensor = self.sensorData[sensor_idx]


        f = sensor.plotIMU(show =False)
        f.suptitle('Please Select two trim points with mouse.  Press right mouse button to undo.', fontsize=14)
        f.show()
        trim_pts = []

        #TODO make trim points keep asking until satisified
        trim_pts = f.ginput(2, show_clicks=True)

        xlocs = [x[0] for x in trim_pts]
        for x in xlocs:
            for ax in f.axes:
                ax.axvline(x = x)

        satisified = input("Are you satisified with Trimpoints [y/n]:")
        if satisified=='n':
            raise Exception("Trimming failed!")

        else:
            trim_range = (sensor.timestamp >= xlocs[0]*1e6) & (sensor.timestamp <=xlocs[1]*1e6)
            for sensor in self.sensorData:
                sensor.timestamp = sensor.timestamp[trim_range]
                sensor.accn = sensor.accn[trim_range,]
                sensor.gyro = sensor.gyro[trim_range,]


# 'Private functions'
def checkEqual(iterator):
   return len(set(iterator)) <= 1

def tellme(s):
    print(s)
    plt.title(s, fontsize=16)
    plt.draw()


if __name__ == "__main__":
    pilot02 = Session("pilot02", 1)
    pilot02.loadSensorData(resample=True)
    pilot02.trim()
    pilot02.sensorData[0].plotIMU()