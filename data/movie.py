
import os
import glob
import numpy as np
import librosa

class Movie:
    
    title = "Bang! You're Dead"
    year = "1961"
    director = "Alfred Hitchcock"
    
    def __init__(self):
        pass
    
    def __repr__(self):
        return f"Movie(title={self.title}, year={self.year}, director={self.director})"
    
    def frames(self, path="/bin/movie/frames"):
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        if not files: raise FileNotFoundError(f"No files found in this path {path}")
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)
    
    def audio(self, path="bin/movie/audio.wav"):
        if not os.path.exists(path): raise FileNotFoundError(f"Audio file not found at {path}")
        return librosa.load(path, sr=None)