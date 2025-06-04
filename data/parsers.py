import os
import glob
import numpy as np
from tqdm import tqdm
import librosa
import pandas as pd
from scipy.ndimage import gaussian_filter1d

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
    
class Spike(Dataset):
    _unit_second = 0.3
    def __init__(self): super().__init__()

    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "bin/spikes/raw_spikes.parquet")
        return self._preprocess_spikes(pd.read_parquet(path), bin_dur=self._unit_second)
    
    def rescale(self, us: float) -> np.ndarray:
        bins = (np.floor(self.raw.index.values / us) * us)
        return self.raw.groupby(bins).mean()
    
    def _preprocess_spikes(self, spikes_df, bin_dur):
    
        # ends of encoding & baseline
        enc_stop, base_stop = spikes_df['base_start'][0], spikes_df['base_stop'][0]
        
        # binning
        enc_bin_edges = np.arange(0, enc_stop + bin_dur, bin_dur)
        base_bin_edges = np.arange(enc_stop, base_stop + bin_dur, bin_dur)

        # init
        time_by_rates = np.zeros((len(enc_bin_edges)-1,
                                len(spikes_df)))

        col_names = []

        for idx, neur in spikes_df.iterrows():

            col_name = neur['hemi'] + '_' + neur['region'] + '_' + neur['neur_id']
            col_names.append(col_name)

            # get enc rates per bin
            enc_spike_counts, _ = np.histogram(neur['enc_spikes'], bins=enc_bin_edges)
            enc_rates = enc_spike_counts / bin_dur

            # get base rates per bin
            base_spike_counts, _ = np.histogram(neur['base_spikes'], bins=base_bin_edges)
            base_rates = base_spike_counts / bin_dur

            # norm
            base_mean, base_sd = np.mean(base_rates), np.std(base_rates)
            enc_rate_normed = (enc_rates - base_mean)# / base_sd

            # smoothing
            enc_rate_smoothed = gaussian_filter1d(enc_rate_normed, sigma=1)

            # save
            time_by_rates[:, idx] = enc_rate_smoothed

        time_axis = np.arange(0, len(enc_bin_edges)-1) * bin_dur
        
        return pd.DataFrame(time_by_rates, columns=col_names, index=time_axis)