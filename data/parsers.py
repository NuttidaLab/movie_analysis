import os
import glob
import numpy as np
from tqdm import tqdm
import librosa
import pandas as pd

from data.abstract import Dataset

class Frames(Dataset):
    def __init__(self): super().__init__()
    
    def _unit_second(self) -> float: return 1/29.97002997002997
    
    def _load(self):
        # location of the pacakage + bin/movie/frames
        path = os.path.join(os.path.dirname(__file__), "bin/movie/frames")
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        if not files: raise FileNotFoundError(f"No files found in this path {path}")
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)

class Audio(Dataset):
    def __init__(self): super().__init__()
    
    def _unit_second(self) -> float: return 1/48000  # Raw audio is sampled at 48000 Hz
    
    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "bin/movie/audio.wav")
        if not os.path.exists(path): raise FileNotFoundError(f"Audio file not found at {path}")
        samples, sr = librosa.load(path, sr=None)
        return samples
    
class Gaze(Dataset):   
    def __init__(self): super().__init__()

    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "bin/gaze")
        files = sorted(glob.glob(f"{path}/*.csv"))
        if not files: raise FileNotFoundError(f"No gaze files found in this path {path}")
        
        data = []
        for fname in tqdm(files):
            df = pd.read_csv(fname)
            if df.empty: continue
            data.append(df.values)
        
class Spikes(Dataset):