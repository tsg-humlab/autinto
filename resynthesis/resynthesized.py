from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from functools import cached_property
import copy

import textgrid as tg

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
    textgrid: tg.TextGrid
    ips:  list[ResynthesizedIntonationalPhrase]
    vars: ResynthesizeVariables

    def __init__(self, phrase: Phrase, sentence: list[str], **kwargs):
        self.ips: list[ResynthesizedIntonationalPhrase] = []
        self.vars = ResynthesizeVariables()
        self.textgrid = phrase.textgrid

        sentence = deque(sentence)
        for phrase_ip in phrase.ips:
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence, self)
            self.ips.append(ip)

    def decode(self):
        point_list = []
        for ip in self.ips:
            ip.decode(point_list)
        return point_list


    def decode_into_textgrid(self):
        textgrid = copy.deepcopy(self.textgrid)

        # Add word labels
        word_tier = tg.PointTier('tones', self.textgrid.minTime, self.textgrid.maxTime)
        for ip in self.ips:
            word_tier.addPoint(tg.Point(ip.ip.start_time/1000, ip.initial_boundary.name))
            for word in ip.words:
                word_tier.addPoint(tg.Point(word.vp_start/1000, word.name))
            word_tier.addPoint(tg.Point(ip.ip.end_time/1000, ip.final_boundary.name))
        textgrid.append(word_tier)

        # Generate the new frequency points
        point_list = self.decode()

        target_tier = tg.PointTier('targets', self.textgrid.minTime, self.textgrid.maxTime)
        frequency_tier = tg.PointTier('ToDI-F0', self.textgrid.minTime, self.textgrid.maxTime)

        for frequency_point in point_list:
            target_tier.addPoint(tg.Point(frequency_point.time/1000, frequency_point.label))
            frequency_tier.addPoint(tg.Point(frequency_point.time/1000, str(int(frequency_point.freq))))
        textgrid.append(target_tier)
        textgrid.append(frequency_tier)

        return textgrid


    @cached_property
    def frequency_range(self):
        freq_low = self.vars.fr + self.vars.n - 0.5*self.vars.w
        freq_high = self.vars.fr + self.vars.n + 0.5*self.vars.w

        return FrequencyRange(freq_low, freq_high)
