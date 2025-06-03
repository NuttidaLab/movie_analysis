from abc import ABC, abstractmethod
import numpy as np

class Dataset(ABC):
    
    # Actual experiment duration is:
    exp_duration = 478.847432 # seconds
    
    @abstractmethod
    def _load(self): pass
    
    @property
    def duration(self) -> int: return (self.n_samples - 1) * self._unit_second
    
    def __init__(self):
        self.raw = self._load()
        self.n_samples = len(self.raw)
    
    def __repr__(self):
        title_line = (
            "\033[1;33mTitle   : \033[0m"
            "\033[1;37mBang! You're Dead (1961)\033[0m"
        )
        director_line = (
            "\033[1;33mDirector: \033[0m"
            "\033[1;37mAlfred Hitchcock\033[0m"
        )
        duration_line = (
            "\033[1;33mDuration: \033[0m"
            "\033[1;37m478.847432 seconds\033[0m"
        )
        return f"{title_line}\n{director_line}\n{duration_line}"
    
    def _rescale_indices(self, us: float) -> np.ndarray:
        n_new = int(np.floor(self.exp_duration / us)) + 1
        new_times = np.arange(n_new) * us
        indices = np.floor(new_times / self._unit_second).astype(int)
        indices = np.clip(indices, 0, self.n_samples - 1)
        return indices
    
    def rescale(self, us: float) -> np.ndarray:
        indices = self._rescale_indices(us)
        return self.raw[indices]
