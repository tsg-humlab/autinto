from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resynthesis.resynthesized import ResynthesizedIntonationalPhrase
    from datetime import timedelta
from resynthesis.types import Frequency, FrequencyPoint


@dataclass
class AbstractWord(ABC):
    """
    AbstractWord contains functions and attributes that hold for all words and this can be used even if you wanted to use other words.
    """
    name: str
    _parent: ResynthesizedIntonationalPhrase
    _index: int
    vp: VoicedPortion

    def __init__(self, name, parent, index, vp):
        self.name = name
        self._parent = parent
        self._index = index
        self.vp = vp

        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @abstractmethod
    def from_name(self, name: str):
        raise NotImplementedError


    @property
    def ip(self) -> ResynthesizedIntonationalPhrase:
        return self._parent

    @property
    def initial_boundary(self) -> AbstractInitialBoundary:
        return self._parent.initial_boundary
    @property
    def final_boundary(self) -> AbstractFinalBoundary:
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
        Returns either the start of the next VP, or the IP end if this
        is the last word.
        """

        if self.is_last_word:
            return self.ip.end
        else:
            return self.next_word.vp.start


    @property
    def prev_word(self) -> AbstractWord:
        if self.is_first_word:
           raise AssertionError(
                'Tried to call prev_word on the first word in an IP')

        return self._parent.words[self._index-1]

    @property
    def next_word(self) -> AbstractWord:
        if self.is_last_word:
            raise AssertionError(
                'Tried to call next_word on the last word in an IP')

        return self._parent.words[self._index+1]

    @property
    def frequency_range(self) -> FrequencyRange:
        return self._parent.frequency_range


    @property
    def delayspace(self):
        """
        The delayspace is the duration of the current VP, plus the time from
        there to the next accented VP start or IP end; or, said differently,
        the full available time.
        """
        return self.vp.duration + self.time_to_next_boundary


    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)


@dataclass
class AbstractInitialBoundary(ABC):
    """
    Contains functions and attributes that are used for all initial boundaries even if you wanted to use other ones.
    """
    name: str
    _parent: ResynthesizedIntonationalPhrase

    def __init__(self, name, parent):
        self.name = name
        self._parent = parent
        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @abstractmethod
    def from_name(self, name: str):
        raise NotImplementedError


    @property
    def ip(self) -> IntonationalPhrase:
        return self._parent

    @property
    def phrase(self) -> Phrase:
        return self._parent.parent

    @property
    def first_word(self) -> timedelta:
        return self._parent.words[0]

    @property
    def frequency_range(self) -> FrequencyRange:
        return self._parent.frequency_range

    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)


@dataclass
class AbstractFinalBoundary(ABC):
    """
    Containts functions and attributes that are used for all final boundaries even if you wanted to use other ones.
    """
    name: str
    _parent: ResynthesizedIntonationalPhrase

    def __init__(self, name, parent):
        self.name = name
        self._parent = parent
        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_name(cls, name: str, parent: ResynthesizedIntonationalPhrase):
        raise NotImplementedError

    @property
    def ip(self) -> IntonationalPhrase:
        return self._parent

    @property
    def last_word(self):
        return self._parent.words[-1]

    @property
    def frequency_range(self) -> FrequencyRange:
        return self._parent.frequency_range

    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)
