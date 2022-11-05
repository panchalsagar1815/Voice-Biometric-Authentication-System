# import dependencies for voice biometrics
import pyaudio
import pyttsx3
import os
from glob import glob
# from IPython.display import Audio, display, clear_output
import wave
# from scipy.io.wavfile import read
# from sklearn.mixture import GaussianMixture
from sklearn.mixture import GMM
import numpy as np
import noisereduce as nr
import librosa
import warnings
from sklearn import preprocessing
import python_speech_features as psf
warnings.filterwarnings("ignore")

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(e)

#Calculate and returns the delta of given feature vector matrix
def calculate_delta(array):
    rows, cols = array.shape
    deltas = np.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first = 0
            else:
                first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]]-array[index[0][1]] + (2 * (array[index[1][0]]-array[index[1][1]]))) / 10
    return deltas

#convert audio to mfcc features
def extract_features(audio, rate):
    mfcc_feat = psf.mfcc(audio, rate, 0.025, 0.01, 20, nfft=1200, appendEnergy=True)
    mfcc_feat = preprocessing.scale(mfcc_feat)
    delta = calculate_delta(mfcc_feat)

    #combining both mfcc features and delta
    combined = np.hstack((mfcc_feat, delta))
    return combined