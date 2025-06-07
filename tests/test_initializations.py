import pytest

# import all of your data classes
from data.movie    import Frames, Audio, People
from data.spikes   import Rates
from data.behavior import Gaze

# list every class you want to make sure “just works”
DATA_CLASSES = [
    Frames,
    Audio,
    People,
    # Measures,
    Rates,
    Gaze,
    # Suspense,
]

@pytest.mark.parametrize("klass", DATA_CLASSES)
def test_can_initialize(klass):
    """
    Instantiating each class should not raise, and if it's a Dataset
    should at least have a `raw` attribute and a non-negative length.
    """
    obj = klass()            # fail here if __init__ blows up
    # sanity-check “dataset” classes
    if hasattr(obj, "raw"):
        assert hasattr(obj, "n_samples")
        assert isinstance(obj.n_samples, int)
        # you can also check that your loader actually returned something:
        assert obj.n_samples >= 0
