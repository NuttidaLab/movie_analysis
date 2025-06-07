from data.abstract import Dataset

import os
import numpy as np
import pandas as pd
import pickle

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
