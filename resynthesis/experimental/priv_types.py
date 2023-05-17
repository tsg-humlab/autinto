from typing import NamedTuple, NewType
import tgt

class ResynthPoint(NamedTuple):
    time: int # milliseconds
    label: str
    freq: int # Hz

class Phrase:
    def __init__(self,
                 ips: list,
                 to_time: int = 100, # milliseconds
                 fr: int = 95, # Hz
                 n: int = 120, # Hz
                 w: int = 190, # Hz
                 phrasal_downstep: float = 0.9):
        self.ips = ips
        self.to_time = to_time
        self.fr = fr
        self.n = n
        self.w = w
        self.phrasal_downstep = phrasal_downstep

class IntonationalPhrase(NamedTuple):
    phrase: Phrase
    interval: tgt.core.Interval
    voiced_portions: list[tgt.core.Interval]
