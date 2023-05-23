from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resynthesis.resynthesized import ResynthesizedIntonationalPhrase


@dataclass
class Word:
    name: str
    parent: ResynthesizedIntonationalPhrase
    index: int
    vp: VoicedPortion

    @classmethod
    def from_name(
            cls,
            name: str,
            parent: ResynthesizedIntonationalPhrase,
            index: int,
            vp: VoicedPortion):
        return cls(name, parent, index, vp)


@dataclass
class InitialBoundary:
    name: str
    parent: ResynthesizedIntonationalPhrase

    @classmethod
    def from_name(cls, name: str, parent: ResynthesizedIntonationalPhrase):
        return cls(name, parent)


@dataclass
class FinalBoundary:
    name: str
    parent: ResynthesizedIntonationalPhrase

    @classmethod
    def from_name(cls, name: str, parent: ResynthesizedIntonationalPhrase):
        return cls(name, parent)
