from data.abstract import Dataset
from data.utils.headlines import MOVIE_HEADLINE

import os
import glob
import numpy as np
from tqdm import tqdm

class Frames(Dataset):
    _unit_second = 1/29.97002997002997
    def __init__(self): super().__init__()
    
    def __repr__(self): return MOVIE_HEADLINE
    
    def _load(self):
        # location of the pacakage + bin/movie/frames
        path = os.path.join(os.path.dirname(__file__), "../bin/movie/frames")
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)
    

        