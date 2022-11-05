import pyaudio
import wave
import speech_recognition as speechsr
# from numba.decorators import jit as optional_jit
import os
import pickle
import time
# from scipy.io.wavfile import read
# from scipy.io.wavfile import write

# from IPython.display import Audio, display, clear_output

from main_functions import *

# login user
def login():

    speak('Enter your Name')
    print('Enter your Name: ')
    name = input()
    print('Speak your Password')
    speak('Speak your Password')

    # Voice Authentication
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 4
    FILENAME = "./test.wav"

    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    time.sleep(2.0)
    print('recording...')
    speak('recording...')
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print('finished recording')
    speak('finished recording')

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # saving wav file
    waveFile = wave.open(FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    # converting test audio to speech and extracting password
    r = speechsr.Recognizer()
    file = speechsr.AudioFile(FILENAME)
    user_password = ''
    print(file)
    with file as source:
        audio2 = r.record(source)

    test_password = r.recognize_google(audio2)

    # Removing Background Noise from Audio File
    for path in glob(FILENAME):
        # name1 = path.split('/')[-1]
        # print('Removing Background Noise for:', path)
        # print('Taking Input as:', input_file)

        cnt = 1
        for filename in glob('./voice_database/background_noise/*.wav'):
            file = filename.split('\\')[1]
            # print('Taking noise as:', filename)
            noise_signal, sample_rate = librosa.load(filename, sr=44100)
            if cnt != 1:
                # print('cnt not 1')
                input_signal1, sample_rate2 = librosa.load(path, sr=44100)
                output = nr.reduce_noise(audio_clip=input_signal1, noise_clip=noise_signal)
                librosa.output.write_wav(path, output, 44100)
            else:
                input_signal, sample_rate3 = librosa.load(path, sr=44100)
                output = nr.reduce_noise(audio_clip=input_signal, noise_clip=noise_signal)
                librosa.output.write_wav(path, output, 44100)
                cnt += 1


            # print(source + '/Clean_Voice')
            # os.mkdir(source + '/Clean_Voice')
            # if os.path.exists(source + '/Clean_Voice/' + name1):
            #     # print('Taking Input as: ', name)
            #     input_signal1, sample_rate = librosa.load(source + '/Clean_Voice/' + name1, sr=44100)
            #     output = nr.reduce_noise(audio_clip=input_signal1, noise_clip=noise_signal)
            #     librosa.output.write_wav(source + '/Clean_Voice/' + name1, output, 44100)
            # else:
            #     #     clear noise



            # print('===========')
        # print('Removing Background Noise Complete for:', path)

    # Removing silence from audio file
    for file_n in glob(FILENAME):
        print('Removing Silence from Noise for:', file_n)
        sig, smp_r = librosa.load(file_n, sr=44100)
        yt, index = librosa.effects.trim(sig)
        # yt = yt.astype(np.int32)
        librosa.output.write_wav(file_n, yt, 44100)
        # write(file_n, 44100, yt)


    modelpath = "./gmm_models/"

    gmm_files = [os.path.join(modelpath, fname) for fname in
                 os.listdir(modelpath) if fname.endswith('.gmm')]
    # print('Gmm Files: \n', gmm_files)

    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    # print('Models: \n', models)

    speakers = [fname.split("/")[-1].split(".gmm")[0] for fname
                in gmm_files]
    # print('Speakers: \n', speakers)

    if len(models) == 0:
        print("No Users in the Database!")
        speak("No Users in the Database!")
        return

    # read test file
    audio, sr = librosa.load(FILENAME, sr=44100)
    # sr, audio = read(FILENAME)

    # extract mfcc features
    vector = extract_features(audio, sr)
    # print(vector)
    log_likelihood = np.zeros(len(models))
    # print('log likelihood: \n', log_likelihood)

    # checking with each model one by one
    for i in range(len(models)):
        gmm = models[i]
        scores = np.array(gmm.score(vector))
        # print(scores)
        log_likelihood[i] = scores.sum()

    pred = np.argmax(log_likelihood)
    # print('PRED: \n', pred)
    identity = speakers[pred]
    # print(identity)

    # if voice not recognized than terminate the process
    # if identity == 'unknown':
    #     print('Not Recognized! Try again...')
    #     speak('Not Recognized! Try again...')
    #     return

    # print('Door Unlocked! Welcome', identity)
    # msg = 'Door Unlocked! Welcome'+identity
    # speak(msg)

    if identity == name:

        # print('Welcome ' + name)
        # msg = 'Welcome ' + name
        # speak(msg)
        # print('Now Speak your Password')
        # speak('Now Speak your Password')
        #
        # # Voice Authentication
        # FORMAT = pyaudio.paInt16
        # CHANNELS = 2
        # RATE = 44100
        # CHUNK = 1024
        # RECORD_SECONDS = 3
        # FILENAME_PASSWORD = "./password.wav"
        #
        # audio = pyaudio.PyAudio()
        #
        # # start Recording
        # stream = audio.open(format=FORMAT, channels=CHANNELS,
        #                     rate=RATE, input=True,
        #                     frames_per_buffer=CHUNK)
        #
        # time.sleep(2.0)
        # print('recording...')
        # speak('recording...')
        # frames = []
        #
        # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        #     data = stream.read(CHUNK)
        #     frames.append(data)
        # print('finished recording')
        # speak('finished recording')
        #
        # # stop Recording
        # stream.stop_stream()
        # stream.close()
        # audio.terminate()
        #
        # # saving wav file
        # waveFile = wave.open(FILENAME_PASSWORD, 'wb')
        # waveFile.setnchannels(CHANNELS)
        # waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        # waveFile.setframerate(RATE)
        # waveFile.writeframes(b''.join(frames))
        # waveFile.close()
        #
        # # converting test audio to speech and extracting password
        # r = speechsr.Recognizer()
        # file = speechsr.AudioFile(FILENAME_PASSWORD)
        # user_password = ''
        # print(file)
        # with file as source:
        #     audio2 = r.record(source)
        #
        # test_password = r.recognize_google(audio2)

        with open('./voice_database/'+name+'/password.txt', 'r') as f:
            user_password += f.read()

        print('Train:', user_password)
        print('Test:', test_password)

        if user_password == test_password:
            print('Door Unlocked! Welcome', identity)
            msg = 'Door Unlocked! Welcome' + identity
            speak(msg)
            return
        else:
            print('Wrong Password ' + name)
            msg = 'Wrong Password ' + name
            speak(msg)
            return

    else:
        print('Not Recognized! Try again...')
        speak('Not Recognized! Try again...')
        return


if __name__ == '__main__':
    login()