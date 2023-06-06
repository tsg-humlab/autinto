from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resynthesis.resynthesized import ResynthesizedIntonationalPhrase
    from datetime import timedelta
from resynthesis.types import Frequency, FrequencyPoint, ResynthesizeVariables


@dataclass
class AbstractPitchAccent(ABC):
    """
    Class that all pitch accents derive from.

    It implements a few features that are useful to every pitch accent
    (initial boundaries, words, and final boundaries), and specifies the
    decode() and from_name() method that all pitch accents must
    implement.
    """

    name: str
    _parent: ResynthesizedIntonationalPhrase

    def __init__(self, name, parent):
        self.name = name
        self._parent = parent
        # from_name is called here, anytime a pitch accent
        # is instantiated
        self.from_name(name)

    @abstractmethod
    def decode(self, point_list: list[FrequencyPoint]):
        """
        decode() takes a list of FrequencyPoints (as specified in
        `types.py`), and extends it with more points. These points
        constitute the resynthesis.
        """

        # Classes which derive from this class must implement this.
        raise NotImplementedError

    @abstractmethod
    def from_name(self, name: str):
        """
        from_name() takes a pitch accent name, like 'H*L', and decodes
        it into any variables that may be useful when decoding. The
        legality of supplied pitch accents may also be checked here.

        self.name will also be available in decode(), so it is not
        strictly necessary to do anything here, but note that the method
        must still be implemented even in that case (and then simply
        specified to do nothing.)
        """

        raise NotImplementedError


    @property
    def ip(self) -> ResynthesizedIntonationalPhrase:
        """
        self.ip, mainly used to get the IP start and end (self.ip.start
        and self.ip.end).
        Also used to apply a downstep to the IP, with self.ip.downstep(x).
        """
        return self._parent

    @property
    def phrase(self) -> ResynthesizedPhrase:
        """
        self.phrase: Useful for downstepping the entire phrase.
        """
        return self._parent.parent

    @property
    def vars(self) -> ResynthesizeVariables:
        """
        Used for global variables like Fr (self.vars.fr), FROMTIME
        (self.vars.from_time), etc. See `types.py` for the full list.
        """
        return self._parent.vars

    @property
    def frequency_range(self) -> FrequencyRange:
        """
        The frequency range that frequencies are normally scaled in.
        Does not change within a single word, so we simply use the IP's
        range.
        """
        return self._parent.frequency_range


    def scale_frequency(self, scalar) -> Frequency:
        """
        Helper method to scale frequencies. Call self.scale_frequency(x)
        with x between 0.0 and 1.0 to get a frequency within range. See
        `types.py` for the FrequencyRange implementation.
        """
        return self.frequency_range.scale(scalar)


@dataclass
class AbstractWord(AbstractPitchAccent):
    """
    AbstractWord contains functions and attributes that hold for all words and this can be used even if you wanted to use other words.
    """
    _index: int
    vp: VoicedPortion

    def __init__(self, name, parent, index, vp):
        self._index = index
        self.vp = vp

        super().__init__(name, parent)


    @property
    def initial_boundary(self) -> AbstractInitialBoundary:
        """Reference to the initial boundary of this IP"""
        return self._parent.initial_boundary

    @property
    def final_boundary(self) -> AbstractFinalBoundary:
        """Reference to the final boundary of this IP"""
        return self._parent.final_boundary

    @property
    def is_first_word(self) -> bool:
        return self._index == 0
    @property
    def is_last_word(self) -> bool:
        return self._index == len(self._parent.words) - 1


    @property
    def next_boundary(self) -> timedelta:
        """
        Returns the next boundary after this word: either the next
        word's VP start, or the IP end if there is no next word.
        """
        if self.is_last_word:
            return self.ip.end
        else:
            return self.next_word.vp.start


    @property
    def prev_word(self) -> AbstractWord:
        """The previous word in this IP."""

        # nice errors
        if self.is_first_word:
           raise AssertionError(
                'Tried to call prev_word on the first word in an IP')

        return self._parent.words[self._index-1]

    @property
    def next_word(self) -> AbstractWord:
        """The next word in this IP."""

        if self.is_last_word:
            raise AssertionError(
                'Tried to call next_word on the last word in an IP')

        return self._parent.words[self._index+1]





class AbstractInitialBoundary(AbstractPitchAccent):
    """
    InitialBoundary inherits from this class. It does not implement
    much, currently! (But it is of course, a pitch accent and so has the
    same features as the AbstractPitchAccent defined above.)
    """

    @property
    def first_word(self) -> timedelta:
        """The first word in this IP."""
        return self._parent.words[0]


class AbstractFinalBoundary(AbstractPitchAccent):
    """
    FinalBoundary inherits from this class. It does not implement
    much, currently!
    """

    @property
    def last_word(self):
        """The last word in this IP."""
        return self._parent.words[-1]
