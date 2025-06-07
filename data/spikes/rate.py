from data.abstract import Dataset

import os
import glob
import numpy as np
from tqdm import tqdm
import pandas as pd
from scipy.ndimage import gaussian_filter1d

class Rates(Dataset):
    _unit_second = 0.3
    def __init__(self): super().__init__()

    def _load(self):
        path = os.path.join(os.path.dirname(__file__), "../bin/spikes/raw_spikes.parquet")
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
        time_by_rates = np.zeros((len(enc_bin_edges)-1, len(spikes_df)))

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