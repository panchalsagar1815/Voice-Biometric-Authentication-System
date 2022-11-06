import os
import pickle
import speech_recognition as speechsr
import librosa
import time
from numba.cuda import syncthreads_or
# from setuptools import sic
from main_functions import *

# add new user
def add_user():
    speak('Enter your Name')
    print('Enter your Name: ')
    name = input()
    # msg = 'Welcome'+name
    # speak(msg)
    # check_user = []
    # user = ''
    # for folder_name in glob('./voice_database/*'):
    #     user = folder_name.split('\\')[-1]
    #     check_user.append(user)
    #
    # if name in check_user:
    #     speak('Name Already Exists! Try Another Name...')
    #     print("Name Already Exists! Try Another Name...")
    #     return
    # else:
    #     pass

    # check for existing database
    if os.path.exists('./User_db/embedding.pickle'):
        with open('./User_db/embedding.pickle', 'rb') as database:
            db = pickle.load(database)
            print(db)
            if name in db:
                print('Name Already Exists! Try Another Name...')
                speak('Name Already Exists! Try Another Name...')
                return
    else:
        # if database not exists than creating new database
        db = []

    # Voice authentication
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 4

    source = "./voice_database/" + name
    # source = "./voice_database/" + name + "/Recorded"

    os.mkdir(source)

    k = 1
    for i in range(16):
        audio = pyaudio.PyAudio()

        if i == 0:
            j = 3
            while j >= 0:
                time.sleep(1.0)
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Speak any random sentence {} seconds".format(j))
                msg = 'Speak any random sentence {} seconds"'.format(j)
                speak(msg)
                j -= 1

        elif i <= 14:
            time.sleep(2.0)
            print("Speak any random sentence one more time")
            msg = 'Speak any random sentence one more time'
            speak(msg)
            time.sleep(0.8)

        else:
            time.sleep(2.0)
            print("Speak your password")
            msg = 'Speak your password'
            speak(msg)
            time.sleep(0.8)

        # start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        print("recording...")
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # saving wav file of speaker
        waveFile = wave.open(source + '/' + str((i + 1)) + '.wav', 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        print("Done")
        speak('Done')

        # clean_noise()
        # Removing Background Noise from audio file
        for path in glob(source + '/' + str((i + 1)) + '.wav'):
            name1 = path.split('/')[-1]
            print('Removing Background Noise for:', name1)
            # print('Taking Input as:', input_file)
            input_signal, sample_rate3 = librosa.load(path, sr=44100)
            for filename in glob('./voice_database/background_noise/*.wav'):
                file = filename.split('\\')[1]
                # print('Taking noise as:', filename)
                noise_signal, sample_rate = librosa.load(filename, sr=44100)
                if k == 1:
                    print(source + '/Clean_Voice')
                    os.mkdir(source + '/Clean_Voice')
                    if os.path.exists(source + '/Clean_Voice/' + name1):
                        # print('Taking Input as: ', name)
                        input_signal1, sample_rate = librosa.load(source + '/Clean_Voice/' + name1, sr=44100)
                        output = nr.reduce_noise(audio_clip=input_signal1, noise_clip=noise_signal)
                        librosa.output.write_wav(source + '/Clean_Voice/' + name1, output, 44100)
                    else:
                        #     clear noise
                        output = nr.reduce_noise(audio_clip=input_signal, noise_clip=noise_signal)
                        librosa.output.write_wav(source + '/Clean_Voice/' + name1, output, 44100)
                    k += 1
                else:
                    if os.path.exists(source + '/Clean_Voice/' + name1):
                        # print('Taking Input as: ', name)
                        input_signal1, sample_rate = librosa.load(source + '/Clean_Voice/' + name1, sr=44100)
                        output = nr.reduce_noise(audio_clip=input_signal1, noise_clip=noise_signal)
                        librosa.output.write_wav(source + '/Clean_Voice/' + name1, output, 44100)
                    else:
                        #     clear noise
                        output = nr.reduce_noise(audio_clip=input_signal, noise_clip=noise_signal)
                        librosa.output.write_wav(source + '/Clean_Voice/' + name1, output, 44100)
                # print('===========')
            print('Removing Background Noise Complete for:', name1)


        # Removing silence from audio file
        for file_n in glob(source + '/Clean_Voice/' + str((i + 1)) + '.wav'):
            print('Removing Silence from Noise for:', file_n)
            sig, smp_r = librosa.load(file_n, sr=44100)
            yt, index = librosa.effects.trim(sig)
            librosa.output.write_wav(file_n, yt, 44100)

        dest = "./gmm_models/"
        count = 1

        features = np.asarray(())
        for path in os.listdir(source + '/Clean_Voice'):
            path = os.path.join(source + '/Clean_Voice', path)
            # print(path)

            # reading audio files of speaker
            # (sr, audio) = read(path)
            audio, sr = librosa.load(path, sr=44100)
            print('Recorded Audio:', sr, audio)
            # print('count:', count)

            # extract 40 dimensional MFCC & delta MFCC features
            vector = extract_features(audio, sr)
            # print(vector)

            if features.size == 0:
                features = vector
            else:
                features = np.vstack((features, vector))

            # when features of 3 files of speaker are concatenated, then do model training
            if count == 16:
                gmm = GMM(n_components=16, n_iter=200, covariance_type='diag', n_init=3)
                gmm.fit(features)

                db.append(name)
                pickle.dump(db, open('./User_db/embedding.pickle', 'wb'))

                # saving the trained gaussian model
                pickle.dump(gmm, open(dest + name + '.gmm', 'wb'))
                # print(name + ' added successfully')
                # msg = name + 'has registered successfully'
                # speak(msg)

                features = np.asarray(())
                count = 0
            count = count + 1

    # storing password in password.txt file
    r = speechsr.Recognizer()
    file = speechsr.AudioFile(source + '/16.wav')
    print(file)
    with file as source:
        audio = r.record(source)

    with open('./voice_database/'+name+'/password.txt', 'w') as f:
        f.write(str(r.recognize_google(audio)))

    # print(r.recognize_google(audio))
    print(name + ' added successfully')
    msg = name + 'has registered successfully'
    speak(msg)


if __name__ == '__main__':
    add_user()
    # filename = 'embedding.pickle'
    # # db = {'unknown'}
    # # with open('./User_db/'+filename, 'wb') as f:
    # #     pickle.dump(db, f)
    #
    # with open('./User_db/'+filename, 'rb') as database:
    #     db = pickle.load(database)
    #     print(db)


