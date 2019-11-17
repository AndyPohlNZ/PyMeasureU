#!/usr/bin/python3

from imeasureu import IMeasureU
import warnings


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

        print(sensor_lengths)

        if not checkEqual(sensor_lengths):
            warnings.warn("Not all sensor data provided recorded for the same length.  Are you sure the all sensors are from the same session?", Warning)

    def trim(self):
        
        


def checkEqual(iterator):
   return len(set(iterator)) <= 1


if __name__ == "__main__":
    pilot02 = Session("pilot02", 1)
    pilot02.loadSensorData(resample=True)