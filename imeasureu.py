#!/usr/bin/python3
import sys
import csv
import numpy as np
import time
from statistics import mean
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt


class IMeasureU:
    '''
    Class to handle files from IMeasureU BlueTrident sensors

    Created by: Andy Pohl - andrew.pohl@ucalgary.ca
                University of Calgary
                November 2019
    '''

    EARTH_GRAVITY=9.80665

    #TODO handle Mag....
    def __init__(self, fileloc, name):
        '''
        Initialize an IMeasureU Object

        Args:   fileloc <String>:   A string specifying the location
                                    of the file
        '''
        self.fileloc = fileloc
        self.name = name
        self.type = 'Unknown' # LowG or HighG
        self.recordType = 'Unknown' # DeviceStream or SensorSave.
        self.resampled = False # if object then signal has been resSampled.
        self.recordTime = None # length in seconds
        self.sampleRate = None
        self.timestamp = []
        self.accn = []
        self.gyro = []
        #self.mag = []

    def __str__(self):
        return("IMeasureU Sensor Data for sensor: " + self.name + "\nRecord Type: " + self.type +"-" +self.recordType + "\nSample Rate: " + str(self.sampleRate) + "Hz\nRecording Length: " + str(self.recordTime)+"s")

    def loadData(self):
        '''
        Loads Data from the specified file requied when class was 
        initialized

        Args:   
            None
        
        Returns:
            void
        '''

        file_length = getFileLength(self.fileloc)
        with open(self.fileloc, 'r') as file:
            csvreader = list(csv.reader(file, delimiter=','))
            # Set type
            self.type = csvreader[1][1]

            initial_time = int(csvreader[1][0])

            # Read data into the corresponding columns
            printProgressBar(0, file_length-1, prefix = 'Reading IMU File:', suffix = 'Complete', length = 50)
            line_count = 0
            for row in csvreader:

                if line_count == 0:
                    header = row
                    line_count += 1

                    if 'mag_x (uT)' in header:
                        self.recordType = 'DeviceStream'
                    else:
                        self.recordType = 'SensorSave'
                else:
                    
                    printProgressBar(line_count, file_length-1, prefix = 'Reading IMU File:', suffix = 'Complete', length = 50)

                    float_row = []
                    for col in row:
                        try:
                            float_row.append(float(col))
                        except ValueError:
                            float_row.append(None)

                    self.timestamp.append(int(row[0]) - initial_time) 
                    self.accn.append([float_row[2], float_row[3], float_row[4]])
                    self.gyro.append([float_row[5], float_row[6], float_row[7]])
                    #self.mag.append([float_row[8], float_row[9], float_row[10]])
                    line_count += 1
        file.close()

            
        self.timestamp = np.array(self.timestamp)
        self.accn = np.array(self.accn)
        self.gyro = np.array(self.gyro)
        print()

        # Update recordtime and sample rate
        self.recordTime = float(self.timestamp[-1])/1e6

        periods = [(t - s)/1e6 for s, t in zip(self.timestamp, self.timestamp[1:])]
        self.sampleRate = float(1)/mean(periods)

    def plot(self, sensorType = 'accn', show=True, ax = None):
        '''
        Plots signals from the specified sensor type on an IMU

        Args:
            sensorType <string>: either 'accn', 'gyro' or 'mag' specifying which sensor to plot
            show <bool>: Wheter to show the plot or not.

        Returns:
            plot <matplotlib obj>: sensor plot can be viewed 
        '''
        if not ax:
            f, ax = plt.subplots()

        if sensorType == 'accn':
            ax.plot(self.timestamp/1e6, self.accn[:,0]/self.EARTH_GRAVITY, alpha=0.4)
            ax.plot(self.timestamp/1e6, self.accn[:,1]/self.EARTH_GRAVITY, alpha=0.4)
            ax.plot(self.timestamp/1e6, self.accn[:,2]/self.EARTH_GRAVITY, alpha=0.4)
            ax.legend(['x', 'y', 'z'])
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Acceleration [g]')
            ax.set_ylim([-16.5, 16.5])
            #ax.title('Accelerometer')

        elif sensorType == 'gyro':
            ax.plot(self.timestamp/1e6, self.gyro[:,0], alpha=0.4)
            ax.plot(self.timestamp/1e6, self.gyro[:,1], alpha=0.4)
            ax.plot(self.timestamp/1e6, self.gyro[:,2], alpha=0.4)
            ax.legend(['x', 'y', 'z'])
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Angular Velocity [deg/s]')
            ax.set_ylim([-2000.5, 2000.5])
            #plt.title('Gyroscope')

        # TODO implelment mag plot...
        
        else:
            raise Exception('Specified sensorType not accn, gyro or mag')

        if show:
            plt.show()

        return ax


    def plotIMU(self, show=True):
        '''
        Plots signals from IMU object

        Args:
            None

        Returns:
            void
        '''
        f, (ax21, ax22) = plt.subplots(1,2)
        
        self.plot(sensorType='accn', show=False, ax =ax21)
        #ax21.set_title('Accelerometer')
        # plt.plot(self.timestamp/1e6, self.accn[:,0]/self.EARTH_GRAVITY, alpha=0.4)
        # plt.plot(self.timestamp/1e6, self.accn[:,1]/self.EARTH_GRAVITY, alpha=0.4)
        # plt.plot(self.timestamp/1e6, self.accn[:,2]/self.EARTH_GRAVITY, alpha=0.4)
        # plt.legend(['x', 'y', 'z'])
        # plt.xlabel('Time [s]')
        # plt.ylabel('Acceleration [g]')
        # plt.ylim([-16.5, 16.5])
        # plt.title('Accelerometer')

        self.plot(sensorType='gyro', show=False, ax =ax22)
        #ax22.set_title('Gyroscope')
        # plt.plot(self.timestamp/1e6, self.gyro[:,0], alpha=0.4)
        # plt.plot(self.timestamp/1e6, self.gyro[:,1], alpha=0.4)
        # plt.plot(self.timestamp/1e6, self.gyro[:,2], alpha=0.4)
        # plt.legend(['x', 'y', 'z'])
        # plt.xlabel('Time [s]')
        # plt.ylabel('Angular Velocity [deg/s]')
        # plt.ylim([-2000.5, 2000.5])
        # plt.title('Gyroscope')
        if show:
            plt.show()
        return f


    def resample(self, desiredSampleRate=200):
        ''' 
        Resamples signals to desiredSample Rate via first interpolating with cubic splines
        then resampling at new fequency.

        Args:
            desiredSampleRate <int>: The new desired sample rate 
        '''
        
        if desiredSampleRate < self.sampleRate:
            print("Downsampling from %.2f Hz to %.2f Hz" % (self.sampleRate, desiredSampleRate))
        else:
            print("Upsampling from %.2f Hz to %.2f Hz" % (self.sampleRate, desiredSampleRate))


        new_timestamp = np.arange(0,self.recordTime*1e6, (1/desiredSampleRate)*1e6)

        f_accn = []
        f_gyro = []
        for i in range(3):
            f_accn.append(interp1d(self.timestamp, self.accn[:,i], kind='cubic'))
            f_gyro.append(interp1d(self.timestamp, self.gyro[:,i], kind='cubic'))
        
        accn_resample = np.empty((len(new_timestamp), 3))
        gyro_resampe = np.empty((len(new_timestamp), 3))
        for i in range(3):
            accn_resample[:,i] = f_accn[i](new_timestamp)
            gyro_resampe[:,i] = f_gyro[i](new_timestamp)

        # Reset IMU object
        self.timestamp = new_timestamp
        self.sampleRate = desiredSampleRate
        self.accn = accn_resample
        self.gyro = gyro_resampe
        self.resampled = True

    def filterSignal(self, order, cutoff, signal = 'accn', passType = 'low', type='butter'):
        '''
        Filters the acceleration signal at the given lpcutoff frequency

        Args:
            order <int> order of filter
            cutoff <int> cutoff freq for filter
            passType <string> currently only low pass filtering implemented
            type <string> Type of filter, currently only butterworth implemented.

        Returns:
            Void
        '''

        if type != 'butter':
            raise Exception("Sorry only butterworth filtering implemented.")

        sf = self.sampleRate

        if passType == 'low':
            Wn = lpcutoff/(fs/2)
            b, a = butter(order/2, Wn, btype = 'lowpass')
        
        #TODO implement high pass and band pass filters.

        # apply filter
        if signal == 'accn':
            for i in range(3):
                self.accn[:,i] = filtfilt(b,a, self.accn[:,i])
        elif signal == 'gyro':
            for i in range(3):
                self.gyro[:,i] = filtfilt(b,a, self.gyro[:,i])
        



    def save(self, filename, location, type='csv'):
        '''
        Saves the IMU object to disk at the specified file location.
        
        Args:
            filename <string>: Name of the file.
            location <string>: Desired location of saved file
            type <string>: type='csv' will save a csv file, type='obj' will pickle the object.
        '''

        if location[-1] != '/':
            location += '/'

        filename = location + filename
        if type =='csv':
            # add csv extension to filename
            if filename[-4:]!= '.csv':
                filename += '.csv'
        

            towrite = np.column_stack((self.timestamp, self.accn, self.gyro))
            header = "time_[us],ax_[m/s/s] ,ay_[m/s/s],az_[m/s/s],gx_[deg/s],gy_[deg/s],gz_[deg/s]"
            
            np.savetxt(filename,towrite, delimiter=',', header=header, comments='')
        elif type =='obj':
            from pickle import dump
            # add custom file extension to filename
            if filename[-4:]!= '.imu':
                filename += '.imu'

            with open(filename, 'w') as file:
                dump(self, file)
        
        else:
            raise Exception("Cannot save file of type %s." % type)

    #TODO Filtering method


# Private functions:

def getFileLength(filename):
    with open(filename) as f:
        filelength =  sum(1 for line in f)
        f.close()
        return(filelength)


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == '__main__':
    fileloc = input("Specify location of IMU file: ")
    name = input("Specify a name for the Sensor: ")
    IMU = IMeasureU(fileloc, name)
    print(IMU.fileloc)

    IMU.loadData()
    print(IMU)
    IMU.plotIMU()


                
