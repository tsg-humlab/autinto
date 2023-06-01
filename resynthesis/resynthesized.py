from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from functools import cached_property

from resynthesis.phrase import Phrase, IntonationalPhrase
from resynthesis.pitch_accents import Word, InitialBoundary, FinalBoundary
from resynthesis.types import ResynthesizeVariables, FrequencyRange


@dataclass
class ResynthesizedIntonationalPhrase:
    ip: IntonationalPhrase
    parent: ResynthesizedPhrase

    initial_boundary: InitialBoundary
    words: list[Word]
    final_boundary: FinalBoundary

    def __init__(self, phrase_ip: IntonationalPhrase, sentence: deque[str], parent: ResynthesizedPhrase):
        self.ip = phrase_ip
        self.parent = parent
        str_initial_boundary = sentence.popleft()
        self.initial_boundary = InitialBoundary(str_initial_boundary, self)

        self.words: list[Word] = []
        for voiced_portion in phrase_ip.vps:
            str_word = sentence.popleft()
            if str_word:
                word = Word(str_word,
                            self,
                            len(self.words),
                            voiced_portion)
                self.words.append(word)

        str_final_boundary = sentence.popleft()
        self.final_boundary = FinalBoundary(str_final_boundary, self)

    def decode(self, point_list):
        self.initial_boundary.decode(point_list)
        for word in self.words:
            word.decode(point_list)
        self.final_boundary.decode(point_list)

    @property
    def ip_start(self):
        return self.ip.start_time
    @property
    def ip_end(self):
        return self.ip.end_time

    @property
    def frequency_range(self):
        return self.parent.frequency_range



@dataclass
class ResynthesizedPhrase:
    ips:  list[ResynthesizedIntonationalPhrase]
    vars: ResynthesizeVariables

    def __init__(self, phrase: Phrase, sentence: list[str], **kwargs):
        self.ips: list[ResynthesizedIntonationalPhrase] = []
        self.vars = ResynthesizeVariables()

        sentence = deque(sentence)
        for phrase_ip in phrase.ips:
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence, self)
            self.ips.append(ip)

    def decode(self):
        point_list = []
        for ip in self.ips:
            ip.decode(point_list)
        return point_list


    @cached_property
    def frequency_range(self):
        freq_low = self.vars.fr + self.vars.n - 0.5*self.vars.w
        freq_high = self.vars.fr + self.vars.n + 0.5*self.vars.w

        return FrequencyRange(freq_low, freq_high)
