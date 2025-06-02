
import os
import glob
import numpy as np
import librosa

class Movie:
    
    def __init__(self):
        pass
    
    def __repr__(self):
        return '''
            Title: "Bang! You're Dead (1961)"
            Director: "Alfred Hitchcock"
            Duration: 478.847432 seconds
        '''
    
    def frames(self, path="/bin/movie/frames"):
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        if not files: raise FileNotFoundError(f"No files found in this path {path}")
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)
    
    def audio(self, path="bin/movie/audio.wav"):
        if not os.path.exists(path): raise FileNotFoundError(f"Audio file not found at {path}")
        return librosa.load(path, sr=None)