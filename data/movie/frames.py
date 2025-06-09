from data.abstract import Dataset
from data.utils.headlines import MOVIE_HEADLINE
from data.utils import rescale_sum, rescale_mean

import os
import glob
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
from types import SimpleNamespace

class Frames(Dataset):
    _unit_second = 1/29.97002997002997
    def __init__(self): super().__init__()
    
    def __repr__(self): return MOVIE_HEADLINE
    
    def _load(self):
        # location of the pacakage + bin/movie/frames
        path = os.path.join(os.path.dirname(__file__), "../bin/movie/frames")
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)
    
    @property
    def cuts(self) -> SimpleNamespace:
        camera_cuts = np.load(os.path.join(os.path.dirname(__file__), "../bin/movie/camera_cuts.npy"))
        scene_cuts = np.load(os.path.join(os.path.dirname(__file__), "../bin/movie/scene_cuts.npy"))
        return SimpleNamespace(camera=Dataset.from_array(camera_cuts, 0.3), scene=Dataset.from_array(scene_cuts, 0.3))
    
    @property
    def objects(self) -> SimpleNamespace:
        return SimpleNamespace(people_count=People())
    
    @property
    def measures(self) -> SimpleNamespace:
        df = pd.read_parquet(os.path.join(os.path.dirname(__file__), "../bin/movie/measures.parquet"))
        
        # l1, l2, ssim, wasserstein, correlation, cosine
        return SimpleNamespace(
            l1          = Dataset.from_array(df.l1.values, self._unit_second, rescalar=rescale_sum),
            l2          = Dataset.from_array(df.l2.values, self._unit_second, rescalar=rescale_sum),
            cosine      = Dataset.from_array(df.cosine.values, self._unit_second, rescalar=rescale_sum),
            ssim        = Dataset.from_array(df.ssim.values, self._unit_second, rescalar=rescale_sum),
            wasserstein = Dataset.from_array(df.wasserstein.values, self._unit_second, rescalar=rescale_sum),
            correlation = Dataset.from_array(df.correlation.values, self._unit_second, rescalar=rescale_sum),
        )
        
        
    
class People(Dataset):
    _unit_second = 1/30  # People data is sampled at 30 Hz
    def __init__(self): super().__init__()

    def _load(self) -> np.ndarray:
        # with open('bin/movie/short_faceannots.pkl', 'rb') as f:
        path = os.path.join(os.path.dirname(__file__), "../bin/movie/short_faceannots.pkl")
        with open(path, 'rb') as f:
            short_faceannots = pickle.load(f)
        d = {"frame": [],"people": [],}
        for key, item in short_faceannots.items():
            d['frame'].append(int(key.split('_')[1]))
            d['people'].append(len(item.keys()))
            
        df = pd.DataFrame(d)
        df["time_s"]   = df["frame"] / 25.0
        df["frame30"] = np.floor(df["time_s"] * 29.97002997002997).astype(int)
        raw_people = np.zeros((14351))
        raw_people[df.frame30.values] = df.people.values
        return raw_people