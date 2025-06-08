from data.abstract import Dataset
from data.utils import calculate_volume_and_timbre

import os
import glob
import numpy as np
import librosa
from types import SimpleNamespace
import pandas as pd

class Audio(Dataset):
    # Raw audio is sampled at 48000 Hz
    _unit_second = 1/48000 
    _base_path = os.path.dirname(__file__)
    
    def __init__(self): super().__init__()
    
    def _load(self):
        samples, sr = librosa.load(os.path.join(self._base_path, "../bin/movie/audio/audio.wav"), sr=None)
        return samples

    @property
    def instruments(self):
        volume, timbre = calculate_volume_and_timbre(os.path.join(self._base_path, "../bin/movie/audio/accompaniment.wav"))
        return SimpleNamespace(volume=volume, timbre=timbre)

    @property
    def vocals(self):
        volume, timbre = calculate_volume_and_timbre(os.path.join(self._base_path, "../bin/movie/audio/vocals.wav"))
        
        # According to 3loi/SER-Odyssey-Baseline-WavLM-Multi-Attributes
        vocal_regress = np.load(os.path.join(self._base_path, "../bin/movie/audio/vocal_attributes.npy"))
        arousal = Dataset.from_array(vocal_regress[:, 0], 0.3)
        dominance = Dataset.from_array(vocal_regress[:, 1], 0.3)
        valence = Dataset.from_array(vocal_regress[:, 2], 0.3)
        
        # According to 3loi/SER-Odyssey-Baseline-WavLM-Categorical-Attributes
        # {0: 'Angry',1: 'Sad',2: 'Happy',3: 'Surprise',4: 'Fear',5: 'Disgust',6: 'Contempt',7: 'Neutral'}
        emotions = pd.read_parquet(os.path.join(self._base_path, "../bin/movie/audio/vocal_emos.parquet"))
        
        # make seperate array for each emotion
        angry = Dataset.from_array(emotions['Angry'].to_numpy(), 0.3)
        sad = Dataset.from_array(emotions['Sad'].to_numpy(), 0.3)
        happy = Dataset.from_array(emotions['Happy'].to_numpy(), 0.3)
        surprise = Dataset.from_array(emotions['Surprise'].to_numpy(), 0.3)
        fear = Dataset.from_array(emotions['Fear'].to_numpy(), 0.3)
        disgust = Dataset.from_array(emotions['Disgust'].to_numpy(), 0.3)
        contempt = Dataset.from_array(emotions['Contempt'].to_numpy(), 0.3)
        neutral = Dataset.from_array(emotions['Neutral'].to_numpy(), 0.3)
        
        return SimpleNamespace(volume=volume, timbre=timbre, 
                               arousal=arousal, dominance=dominance, valence=valence, 
                               angry=angry, sad=sad, happy=happy, surprise=surprise, 
                               fear=fear, disgust=disgust, contempt=contempt, 
                               neutral=neutral)
    
        
        
        