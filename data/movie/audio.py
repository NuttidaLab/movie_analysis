from data.abstract import Dataset
from data.utils import calculate_volume_and_timbre

import os
import glob
import numpy as np
import librosa
from types import SimpleNamespace
# from dataclasses import dataclass

# @dataclass
# class Source:
#     volume: Dataset
#     timbre:  Dataset

class Audio(Dataset):
    # Raw audio is sampled at 48000 Hz
    _unit_second = 1/48000 
    _base_path = os.path.dirname(__file__)
    
    def __init__(self): super().__init__()
    
    def _load(self):
        samples, sr = librosa.load(os.path.join(self._base_path, "../bin/movie/audio.wav"), sr=None)
        return samples

    @property
    def instruments(self):
        volume, timbre = calculate_volume_and_timbre(os.path.join(self._base_path, "../bin/movie/accompaniment.wav"))
        return SimpleNamespace(volume=volume, timbre=timbre)

    @property
    def vocals(self):
        volume, timbre = calculate_volume_and_timbre(os.path.join(self._base_path, "../bin/movie/vocals.wav"))
        return SimpleNamespace(volume=volume, timbre=timbre)
    
        
        
        