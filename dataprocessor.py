import librosa
import os
import glob
import numpy as np
import logging

SR = 250
N_FFT = 512 # default 2048 for music, in speech processing, the recommended value is 512, corresponding to 23 milliseconds at a sample rate of 22050 Hz.


logging.basicConfig(filename="dataset1.log", filemode="w", format="%(asctime)s %(message)s", datefmt="%d-%m-%Y %H:%M:%S", level=logging.DEBUG)

def get_spec(paths, author):
    # stdata = []
    for path in paths:
        y, sr = librosa.load(path, sr=SR)
        stft = librosa.core.stft(y=y, n_fft=N_FFT, hop_length=None)
        stft = np.abs(stft)

        spec = librosa.feature.melspectrogram(sr=SR, S=stft, n_fft=N_FFT, power=2.0)
        logmelspec = librosa.power_to_db(spec)
        logmelspec = logmelspec[:, :]
        #logmelspec = logmelspec[np.newaxis, :, :]
        filename = path.split("/")[-1]
       #  print(logmelspec.shape)
        # stdata.append(logmelspec)
        data = {'author': author, 'filename': filename, 'logmel': logmelspec}
        print(data)
        logging.info(filename + " has been saved, array shape: (" + str(logmelspec.shape) + ")")
       # np.save("./data/" + author + "_" + filename + ".npy", data)
        np.save("/Users/ElevenYao/Desktop/data1" + author + "_" + filename + ".npy", data)
        #np.savez("data1.npz", **data)

path = os.path.join(os.path.dirname(os.getcwd()), 'annotatedLibrary')

folder = []
for d in os.listdir(path):
    if (not d.startswith('0')) and os.path.isdir(os.path.join(path, d)):
        folder.append(os.path.join(path, d))
logging.info(">> Paths going to unfold: " + ",".join(folder))
logging.info("********************************")

for f in folder:
    print(f)
    author = f.split("/")[-1]
    logging.info(">> Author: " + author)
    paths = os.path.join(f, "wav")
    paths = glob.glob(paths + "/*.wav")
    logging.info(">> WAV path: paths")
    logging.info("~~~~~~~~~~~~~~~~~start to get spectrograms from "+ author +"~~~~~~~~~~~~~~~~~~~~~~")
    get_spec(paths, author)
    logging.info("~~~~~~~~~~~~~~~~~~"+ author +" finished~~~~~~~~~~~~~~~~~~~~~~")

