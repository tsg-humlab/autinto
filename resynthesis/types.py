from datetime import timedelta
from dataclasses import dataclass

def Seconds(seconds: float):
    return timedelta(seconds=seconds)

def Milliseconds(milliseconds: int):
    # used to be a type
    return timedelta(milliseconds=milliseconds)

Frequency = int # in Hz
FrequencyDiff = Frequency
Scalar = float

@dataclass
class Interval:
    start_time: timedelta
    end_time:   timedelta

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



@dataclass
class FrequencyRange:
    low: Frequency
    width: FrequencyDiff

    def __init__(self, freq_low, freq_high):
        self.low = freq_low
        self.width = freq_high - freq_low

    def scale(self, scalar: float) -> Frequency:
        return self.low + scalar * self.width


@dataclass
class FrequencyPoint:
    label: str
    freq: Frequency
    time: timedelta


@dataclass
class ResynthesizeVariables:
    to_time: timedelta = Milliseconds(90)
    from_time: timedelta = Milliseconds(100)
    star_time: Scalar = 0.3

    phrasal_downstep: Scalar = 0.9
    accentual_downstep: Scalar = 0.7

    fr: Frequency = 95
    n:  Frequency = 120
    w:  FrequencyDiff = 190

    #def __init__(self, kwargs):
        #for key in self.__dataclass_fields__.keys():
            #try:
                #self.__dict__[key] = kwargs[key]
            #except Exception:
                #pass
