#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
About this script [...]


Created on Wed Dec 12 10:55:24 2018

@author: Giulio Gabrieli
"""

###############################################################################
#                                                                             #
#                               Libraries import                              #
#                                                                             #
###############################################################################

import math
import numpy as np
import random
import wave
import struct

random.seed(16081991) #used for consistency

basepath = '/media/giulio/HOME/Articles & Presentation/2019/Praat@LAC2019/' #this is the folder in which to save generated files

samplerate = 44100 #samplerate of the signal
length = 5 #length in seconds of the signals to generate
amplitudeFactors = 6 #ratio between the intensity of f0 and f4 - Cry signals formants' intensity decreases almost linearly
ampMultiplier = 8000.0 #multiplier amplitude

'''
Each entry of the dict files is a file to generate. F0 is the fundamental frequency, 
Noise indicates wheter white noise has to be added, halfF0 if a noise with a frequency
at about half of F0 has to be added and filename is the name of the ooutput file.
'''
files = {0:{"F0": 440, "noise":True,"halfF0":False, "Filename":"A"},
         1:{"F0": 440, "noise":True,"halfF0":True, "Filename":"B"},
         2:{"F0": 575, "noise":True,"halfF0":False, "Filename":"C"},
         3:{"F0": 575, "noise":True,"halfF0":True, "Filename":"D"}}

###############################################################################
#                                                                             #
#                                   Functions                                 #
#                                                                             #
###############################################################################

def sinewave(frequency, amplitude, samplerate, samples):
    ''' This function generate a sine Wave of a specific frequency of a specific length.
        
        * Input:
            * Description of the Input
        * Output: 
            * Description of the output
        
        :param frequency: frequency of the signal to generate
        :type frequency: int
        :param amplitude: amplitude of the signal to generate
        :type amplitude: int        
        :param samplerate: samplerate of the signal to generate
        :type samplerate: int
        :param samples: number of total samples of the signal to generate
        :type samples: int        
        
        :return: sine wave of specified frequency, samplerate, amplitude and length
        :rtype: list
    '''
    
    period = int(samplerate / frequency) #evaluate the period of the signal
    table = [amplitude * math.sin(2*math.pi*frequency * (i%period / samplerate)) for i in range(0,period)] #create a periodic table
    return([table[i%period] for i in range(0, samples)]) #generate a periodic signal of specific lenght (in samples)
    
def white_noise(amplitude,nSamples):    
    ''' This function generate white noise of a specific length.
        
        * Input:
            * Description of the Input
        * Output: 
            * Description of the output
        
        :param amplitude: amplitude of the noise to generate
        :type frequency: int
        :param nSamples: total number of samples of the signal to generate
        :type nSamples: int        
        
        :return: noise of specified amplitude and length
        :rtype: list
    '''
    
    return ([float(amplitude) * random.uniform(-1, 1)  for i in range(0,nSamples)])

def generate_file(frequency, samplerate, length, amplitudeFactors, ampMultiplier,filename,randomrange=20,noise = True,halff0=False):
    ''' This function generate an audio file with the above parameters
        
        * Input:
            * Description of the Input
        * Output: 
            * Description of the output
        
        :param frequency: fundamental frequency of the signal to generate
        :type frequency: int      
        :param samplerate: samplerate of the signal to generate
        :type samplerate: int
        :param length: length of the signal in seconds
        :type length: int                
        :param amplitudeFactors: ratio to which the frequency of the amplitudes decreases
        :type amplitudeFactors: int
        :param ampMultiplier: amplifier ratio of the signal
        :type ampMultiplier: int
        :param filename: filename for the output file
        :type filename: string
        :param randomrange: maximum difference in Hz between the perfect forman frequency and generate value 
        :type randomrange: int
        :param noise: This indicates wheter noise has to be added
        :type noise: boolean
        :param noise: This indicates wheter a noise band at about half of F0 has to be added to the signal
        :type noise: boolean
        
        :return: success of the process 
        :rtype: boolean    
    '''
    
    nSamples = samplerate * length #total number of seconds to generate
    
    formants = [frequency * 2+random.randint(randomrange*-1,randomrange), 
                frequency*3+random.randint(randomrange*-1,randomrange),
                frequency*4+random.randint(randomrange*-1,randomrange),
                frequency*5+random.randint(randomrange*-1,randomrange),
                frequency*6+random.randint(randomrange*-1,randomrange)] #Get some random values for the formants
    
    f0 = np.array(sinewave(frequency,1,44100,nSamples)) #generate the fundamental frequency 
    f1 = np.array(sinewave(formants[0],1 / amplitudeFactors * 5,44100,nSamples)) #generate the formants
    f2 = np.array(sinewave(formants[1],1 / amplitudeFactors * 4,44100,nSamples))
    f3 = np.array(sinewave(formants[2],1 / amplitudeFactors * 3,44100,nSamples))
    f4 = np.array(sinewave(formants[3],1 / amplitudeFactors * 2,44100,nSamples))
    f5 = np.array(sinewave(formants[4],1 / amplitudeFactors,44100,nSamples))
    
    returnDict = {"Filename":filename,"Saved":True,"F0":frequency,"Formants":formants} #initialize a dictionary to return, with computed Formants values
    
    signal =f0+f1+f2+f3+f4+f5 #generate an unique signal
    
    if noise: #if noise has to be added
        noisesig = white_noise(0.3,nSamples) #generate a noise signal
        signal =signal+noisesig #sum signal and noise
        
    if(halff0): #if a noise at half of F0 has to be added
        halff0value = frequency / 2 +random.randint(randomrange*-1,randomrange) #compute a random signal with frequency F0/2+-randomrange
        signal = signal +  np.array(sinewave(halff0value ,1 / amplitudeFactors * 3,44100,nSamples)) #generate the noise and add it to the original signal
        returnDict["halfF0"] = halff0value #add the frequency info to our return dict
       

    ''' Time toamplify and save the generated signal to file'''
    wav_file = wave.open(basepath +filename+'.wav', "w") #open a wav file 
    wav_file.setparams((1, 2, samplerate, len(signal), "NONE", "not compressed")) #set some parameters
    for s in signal: #for each sample
        wav_file.writeframes(struct.pack('h', int(s*ampMultiplier/2))) #amplify it and write it out
    wav_file.close() #close the file 
    
    return(returnDict) #give us some info
        
if(__name__=='__main__'):
    
    for file in files: #for each file to generate, run generate_file
        print(generate_file(files[file]["F0"],
                            samplerate, 
                            length, 
                            amplitudeFactors, 
                            ampMultiplier,
                            filename=files[file]["Filename"],
                            halff0=files[file]["halfF0"],
                            noise=files[file]["noise"]))