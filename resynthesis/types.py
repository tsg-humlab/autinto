"""
The Types module defines some functions and classes that are used in
many of the other modules.
"""

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
    # used to be a type; hence the upper case name. (same for Seconds for consistency)
    return timedelta(milliseconds=milliseconds)


Frequency = int # in Hz
FrequencyDiff = Frequency
Scalar = float


@dataclass
class Interval:
    """
    An Interval is a duration of time with a start_time and end_time.
    """
    start_time: timedelta
    end_time:   timedelta

    @property
    def start(self):
        """Alias for start_time; 'self.vp.start_time' felt too long."""
        return self.start_time

    @property
    def end(self):
        """Alias for end_time."""
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
        """
        Interval.scale(x) returns a time scaled 'x' into an interval.

        For example, scale(0.0) will return the start of the interval,
        scale(0.5) will return the point precisely in the middle, and
        scale(1.0) will return the end of the interval.
        """

        return self.start + scalar * self.duration

def Duration(start_time: timedelta, end_time: timedelta) -> timedelta:
    """
    Slightly shorter syntax for creating an Interval, and then asking for
    its duration.

    Essentially syntax suger for (end_time - start_time).
    """

    return Interval(start_time, end_time).duration


@dataclass
class FrequencyRange:
    """
    A FrequencyRange stores the low and high frequency bounds, and is
    used to scale new FrequencyPoints in the decoding/resynthesizing
    process.
    """

    _low: Frequency
    _width: FrequencyDiff

    def __init__(self, freq_low, freq_high):
        self._low = freq_low
        self._width = freq_high - freq_low

    def scale(self, scalar: float) -> Frequency:
        """Get a frequency in the range [low, high]"""
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


# The following two classes are the ones that can be put into point_list
# during decoding.

@dataclass
class FrequencyPoint:
    """
    A FrequencyPoint has a label, a frequency, and a time. It creates a
    point for Praat resynthesis.
    """

    label: str
    freq: Frequency
    time: timedelta


@dataclass
class AddTime:
    """
    AddTime is used for the final lengthening. It defines an existing
    interval, and the interval that it should change to.

    (Note that the lengthening only listens to the *duration* of the
     new_interval, so attempting to reposition the start time will not
     work.)
    """

    old_interval: Interval
    new_interval: Interval


# The following class contains the custom parameters that can a user may
# change.

@dataclass
class ResynthesizeVariables:	
    """
    The global variables that are used in the resynthesis rules.
    """

    # In `views.py`, the web request is translated into the format defined
    # here below, which is then passed to the ResynthesizedPhrase in
    # `resynthesized.py`. This will then add the frequencies for any gender
    # it finds in the TextGrid, if the user did not specify any values,
    # and will leave all other options blank.
    #
    # Those will then be initialised to the default values defined here.
    #
    # To change the default values, edit them right here. Note that the
    # default frequencies will be overridden if a gender label was found
    # in the TextGrid; to alter those default values, edit the __init__()
    # method of ResynthesizeVariables in `resynthesized.py`.
    #
    # Lastly, to add more default variables, or to remove some, you will
    # have to add or remove them here, and also change the translation
    # of the web request into these variables in `views.py`.


    to_time: timedelta = Milliseconds(130)
    from_time: timedelta = Milliseconds(100)
    star_time: Scalar = 0.3

    phrasal_downstep: Scalar = 0.9
    accentual_downstep: Scalar = 0.7

    fr: Frequency = 95
    n:  Frequency = 120
    w:  FrequencyDiff = 190
