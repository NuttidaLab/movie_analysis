from data.abstract import Dataset

import os
import glob
import numpy as np
import librosa


class Audio(Dataset):
    _unit_second = 1/48000 # Raw audio is sampled at 48000 Hz
    def __init__(self): super().__init__()
    
    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "../bin/movie/audio.wav")
        samples, sr = librosa.load(path, sr=None)
        return samples