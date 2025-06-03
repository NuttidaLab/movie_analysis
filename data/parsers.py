import os
import glob
import numpy as np
from tqdm import tqdm
import librosa
import pandas as pd

from data.abstract import Dataset

class Frames(Dataset):
    _unit_second = 1/29.97002997002997
    def __init__(self): super().__init__()
    
    def _load(self):
        # location of the pacakage + bin/movie/frames
        path = os.path.join(os.path.dirname(__file__), "bin/movie/frames")
        files = sorted(glob.glob(f"{path}/_part*.npy"))
        if not files: raise FileNotFoundError(f"No files found in this path {path}")
        return np.concatenate([ np.load(fname) for fname in tqdm(files) ], axis=0)

class Audio(Dataset):
    _unit_second = 1/48000 # Raw audio is sampled at 48000 Hz
    def __init__(self): super().__init__()
    
    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "bin/movie/audio.wav")
        if not os.path.exists(path): raise FileNotFoundError(f"Audio file not found at {path}")
        samples, sr = librosa.load(path, sr=None)
        return samples
    
class Gaze(Dataset):
    _unit_second = 0.002  # Gaze data is sampled at 500 Hz, which is 0.002 seconds per sample
    def __init__(self): super().__init__()

    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "bin/gaze")
        files = sorted(glob.glob(f"{path}/*.parquet"))
        if not files: raise FileNotFoundError(f"No gaze files found in this path {path}")
        data = [pd.read_parquet(fname) for fname in tqdm(files)]
        tdf = pd.concat(data, ignore_index=True)
        return self._preprocess_gaze(tdf, self._unit_second)
    
    def rescale(self, us: float) -> np.ndarray:
        indices = self._rescale_indices(us)
        return self.raw.iloc[indices]
    
    def _preprocess_gaze(self, df, unit_scale=0.002):
        all_times = np.concatenate(df['RecTime'].values)
        t_min, t_max = all_times.min(), all_times.max()
        common_index = np.arange(t_min, t_max + 1e-9, unit_scale)

        aligned_dfs = []
        for _, row in df.iterrows():
            sess_name = row['sess']  # e.g. "P41CSR1"
            times = np.array(row['RecTime'])
            x = np.array(row['GazeX'])
            y = np.array(row['GazeY'])
            
            # Build a DataFrame indexed by the session’s own rec times:
            temp = pd.DataFrame({'x': x, 'y': y}, index=times)
            
            # Reindex onto the common grid. You can choose method='nearest', 'ffill', or .interpolate():
            temp_reindexed = (
                temp
                .reindex(common_index)                 # puts NaN where exact time is missing
                .interpolate(method='index')           # linear‐interpolate between samples
                #.fillna(method='ffill')               # alternatively, forward‐fill
            )
            
            # Rename the columns so they become x_<sess> and y_<sess>
            temp_reindexed = temp_reindexed.rename(columns={
                'x': f"x_{sess_name}",
                'y': f"y_{sess_name}"
            })
            
            aligned_dfs.append(temp_reindexed)

        return pd.concat(aligned_dfs, axis=1)