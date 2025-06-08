from data.abstract import Dataset

import numpy as np
import librosa

def calculate_volume_and_timbre(path, hop = 512, frame = 2048):
    
    audio_samples, sr = librosa.load(path, sr=None)
    
    # short-time energy (RMS)
    rms = librosa.feature.rms(y=audio_samples, frame_length=frame, hop_length=hop)[0]
    rms_db = librosa.power_to_db(rms**2, ref=np.max)
    # spectral contrast
    contrast = librosa.feature.spectral_contrast(y=audio_samples,sr=sr,n_bands=6,hop_length=hop).mean(axis=0)
    
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)

    # smooth the features
    win = int(1.0 * sr / hop)
    rms_smooth = np.convolve(rms_db, np.ones(win)/win, mode='same')
    contrast_smooth = np.convolve(contrast, np.ones(win)/win, mode='same')
    
    volume_ds = Dataset.from_array(rms_smooth, 512/sr)
    timbre_ds = Dataset.from_array(contrast_smooth, 512/sr)
    return volume_ds, timbre_ds