from abc import ABC, abstractmethod
import numpy as np

class Dataset(ABC):
    
    # Actual experiment duration in seconds
    exp_duration = 478.847432
    
    @property
    @abstractmethod
    def _unit_second(self) -> float: 
        raise NotImplementedError
    
    @abstractmethod
    def _load(self):
        raise NotImplementedError
    
    def __init__(self):
        self.raw = self._load()
        self.n_samples = len(self.raw)
    
    def __repr__(self): return "Dataset Object :)"
    
    @classmethod
    def from_array(cls, array: np.ndarray, unit_second: float):
        class _WrappedDataset(Dataset):
            _unit_second = unit_second
            def _load(self): return array
        return _WrappedDataset()
    
    @property
    def duration(self) -> int: 
        return (self.n_samples - 1) * self._unit_second
    
    def _rescale_indices(self, us: float) -> np.ndarray:
        n_new = int(np.floor(self.exp_duration / us)) + 1
        new_times = np.arange(n_new) * us
        indices = np.floor(new_times / self._unit_second).astype(int)
        indices = np.clip(indices, 0, self.n_samples - 1)
        return indices
    
    def rescale(self, us: float) -> np.ndarray:
        indices = self._rescale_indices(us)
        return self.raw[indices]
