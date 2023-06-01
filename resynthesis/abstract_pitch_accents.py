from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resynthesis.resynthesized import ResynthesizedIntonationalPhrase
from resynthesis.types import Milliseconds, Frequency, FrequencyPoint


@dataclass
class AbstractWord(ABC):
    name: str
    parent: ResynthesizedIntonationalPhrase
    index: int
    vp: VoicedPortion

    def __init__(self, name, parent, index, vp):
        self.name = name
        self.parent = parent
        self.index = index
        self.vp = vp

        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @abstractmethod
    def from_name(self, name: str):
        raise NotImplementedError


    @property
    def vp_start(self) -> Milliseconds:
        return self.vp.start_time
    @property
    def vp_end(self) -> Milliseconds:
        return self.vp.end_time
    @property
    def vp_duration(self) -> Milliseconds:
        return self.vp_end - self.vp_start

    @property
    def time_to_next_boundary(self) -> Milliseconds:
        return self.next_boundary - self.vp_end

    @property
    def next_boundary(self) -> Milliseconds:
        if self.is_last_word:
            return self.ip_end
        else:
            return self.next_vp_start

    @property
    def next_vp_start(self) -> Milliseconds:
        return self.parent.words[self.index+1].vp_start

    @property
    def is_last_word(self) -> bool:
        return self.index + 1 == len(self.parent.words)

    @property
    def ip_start(self) -> Milliseconds:
        return self.parent.ip_start
    @property
    def ip_end(self) -> Milliseconds:
        return self.parent.ip_end

    @property
    def frequency_range(self) -> FrequencyRange:
        return self.parent.frequency_range

    @property
    def final_boundary(self):
        return self.parent.final_boundary.name


    """
    The delayspace is the duration of the current VP, plus the time from
    there to the next accented VP start or IP end; or, said differently,
    the full available time.
    """
    @property
    def delayspace(self):
        return self.vp_duration + self.time_to_next_boundary


    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)


@dataclass
class AbstractInitialBoundary(ABC):
    name: str
    parent: ResynthesizedIntonationalPhrase

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @abstractmethod
    def from_name(self, name: str):
        raise NotImplementedError


    @property
    def time_to_first_word(self) -> Milliseconds:
        return self.parent.words[0].vp_start

    @property
    def ip_start(self) -> Milliseconds:
        return self.parent.ip_start
    @property
    def ip_end(self) -> Milliseconds:
        return self.parent.ip_end
    @property
    def frequency_range(self) -> FrequencyRange:
        return self.parent.frequency_range

    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)


@dataclass
class AbstractFinalBoundary(ABC):
    name: str
    parent: ResynthesizedIntonationalPhrase

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.from_name(name)

    @abstractmethod
    def decode(point_list: list[FrequencyPoint]):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_name(cls, name: str, parent: ResynthesizedIntonationalPhrase):
        raise NotImplementedError


    @property
    def last_word(self):
        return self.parent.words[-1]
    @property
    def frequency_range(self) -> FrequencyRange:
        return self.parent.frequency_range

    def scale_frequency(self, scalar) -> Frequency:
        return self.frequency_range.scale(scalar)

    @property
    def ip_start(self) -> Milliseconds:
        return self.parent.ip_start
    @property
    def ip_end(self) -> Milliseconds:
        return self.parent.ip_end
