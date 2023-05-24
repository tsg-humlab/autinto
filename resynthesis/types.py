from dataclasses import dataclass

Milliseconds = int
Frequency = int # in Hz
FrequencyDiff = Frequency
Scalar = float

@dataclass
class Interval:
    start_time: Milliseconds
    end_time:   Milliseconds

    def __init__(self, start_time: float, end_time: float):
        self.start_time = Milliseconds(start_time*1000)
        self.end_time = Milliseconds(end_time*1000)


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
    time: Milliseconds


@dataclass
class ResynthesizeVariables:
    to_time: Milliseconds = Milliseconds(90)
    from_time: Milliseconds = Milliseconds(100)
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
