from datetime import timedelta
from dataclasses import dataclass

def Seconds(seconds: float):
	"""
	Return timedelta object with seconds
	"""
    return timedelta(seconds=seconds)

def Milliseconds(milliseconds: int):
	"""
	Return timedelta object with milliseconds
	"""
    # used to be a type hence we give the function an upper case name. (same for Seconds for consistency).
    return timedelta(milliseconds=milliseconds)

#here we set the types
Frequency = int # in Hz
FrequencyDiff = Frequency
Scalar = float


@dataclass
class Interval:
	"""
	An interval is a duration of time with a start_time and end_time.
	"""
    start_time: timedelta
    end_time:   timedelta

    @property
    def start(self):
        return self.start_time
    @property
    def end(self):
        return self.end_time
    @property
    def duration(self):
        return self.end - self.start

    def __init__(self, start_time, end_time):
        # Make sure that start_time and end_time are actually timedeltas,
        # and not ints or floats without unit.
        assert (isinstance(start_time, timedelta)
                and isinstance(end_time, timedelta)), \
               'Error instantiating an {}: Expected {}, found {} and {}'.format(
                   type(self).__name__,
                   timedelta,
                   type(start_time),
                   type(end_time)
                )

        self.start_time = start_time
        self.end_time = end_time


    def scale(self, scalar):
		# Here we define the meaning of scale in the case of time.
        return self.start + scalar * self.duration

def Duration(start_time: timedelta, end_time: timedelta) -> timedelta:
    """
    Slightly shorter syntax for creating an interval, then asking for
    its duration.
    """
    return Interval(start_time, end_time).duration


@dataclass
class FrequencyRange:
	"""
	A FrequencyRange is a range with a low freqeuency and width (meaning the difference between low and high frequency).
	"""
    _low: Frequency
    _width: FrequencyDiff

    def __init__(self, freq_low, freq_high):
        self._low = freq_low
        self._width = freq_high - freq_low

    def scale(self, scalar: float) -> Frequency:
		# Here we define the meaning of scale in the case of frequency.
        return self.low + scalar * self.width

    @property
    def low(self):
        return self._low
    @property
    def high(self):
        return self._low + self._width
    @property
    def width(self):
        return self._width


@dataclass
class FrequencyPoint:
	"""
	A FrequencyPoint has a label a frequency and a time (where it is on the interval).
	"""
    label: str
    freq: Frequency
    time: timedelta

@dataclass
class AddTime:
    old_interval: Interval
    new_interval: Interval


@dataclass
class ResynthesizeVariables:	
	"""
	Here we define important variables that are used in the resynthesis rules.
	"""
	to_time: timedelta = Milliseconds(90)
    from_time: timedelta = Milliseconds(100)
    star_time: Scalar = 0.3

    phrasal_downstep: Scalar = 0.9
    accentual_downstep: Scalar = 0.7

    fr: Frequency = 95
    n:  Frequency = 120
    w:  FrequencyDiff = 190
