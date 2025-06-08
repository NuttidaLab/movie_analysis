from data.abstract import Dataset

import os
import glob
import numpy as np
import librosa


class Suspense(Dataset):
    def __init__(self): super().__init__()
    _unit_second = 478.847432/193 # Raw audio is sampled at 48000 Hz
    
    def _load(self):
        return np.load(os.path.join(os.path.dirname(__file__), "../bin/suspense/all_suspense.npy")).T