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
    _frequency_range: FrequencyRange

    def __init__(self, phrase_ip: IntonationalPhrase, sentence: deque[str], parent: ResynthesizedPhrase):
        self.ip = phrase_ip
        self.parent = parent
        
        str_initial_boundary = sentence.popleft()
        self.checkUnaccented(str_initial_boundary, sentence)
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

        # We only set this when the decoding starts
        self._frequency_range = None

    def decode(self, point_list):
        # Reset frequency_range
        self.reset_downstep()

        self.initial_boundary.decode(point_list)
        for word in self.words:
            word.decode(point_list)
        self.final_boundary.decode(point_list)

        self.parent._frequency_range = self.frequency_range

    @property
    def vars(self) -> ResynthesizedVariables:
        return self.parent.vars

    @property
    def start(self):
        return self.ip.start_time
    @property
    def end(self):
        return self.ip.end_time

    @property
    def frequency_range(self):
        if self._frequency_range:
            return self._frequency_range
        else:
            return self.parent.frequency_range

    def downstep(self, scalar):
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)

    def reset_downstep(self):
        self._frequency_range = None
    
    def checkUnaccented(self, str_initial_boundary, sentence):
        if str_initial_boundary in {"H", "L"}:
            sentence.insert(0, None)


@dataclass
class ResynthesizedPhrase:
    textgrid: tg.TextGrid
    ips:  list[ResynthesizedIntonationalPhrase]
    vars: ResynthesizeVariables

    def __init__(self, phrase: Phrase, sentence: list[str], **kwargs):
        self.ips: list[ResynthesizedIntonationalPhrase] = []
        self.textgrid = phrase.textgrid

        gender = self.textgrid.getFirst('words')[0].mark
        match gender:
            case 'm':
                if 'fr' not in kwargs:
                    kwargs['fr'] = 70
                if 'n' not in kwargs:
                    kwargs['n'] = 70
                if 'w' not in kwargs:
                    kwargs['w'] = 110
            case 'v':
                if 'fr' not in kwargs:
                    kwargs['fr'] = 95
                if 'n' not in kwargs:
                    kwargs['n'] = 120
                if 'w' not in kwargs:
                    kwargs['w'] = 190

        self.vars = ResynthesizeVariables(**kwargs)

        sentence = deque(sentence)
        for phrase_ip in phrase.ips:
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence, self)
            self.ips.append(ip)

        freq_low = self.vars.fr + self.vars.n - 0.5*self.vars.w
        freq_high = self.vars.fr + self.vars.n + 0.5*self.vars.w
        self._frequency_range = FrequencyRange(freq_low, freq_high)

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
            word_tier.addPoint(tg.Point(ip.ip.start.total_seconds(), ip.initial_boundary.name))
            for word in ip.words:
                word_tier.addPoint(tg.Point(word.vp.start.total_seconds(), word.name))
            word_tier.addPoint(tg.Point(ip.ip.end.total_seconds(), ip.final_boundary.name))
        textgrid.append(word_tier)

        # Generate the new frequency points
        point_list = self.decode()

        target_tier = tg.PointTier('targets', self.textgrid.minTime, self.textgrid.maxTime)
        frequency_tier = tg.PointTier('ToDI-F0', self.textgrid.minTime, self.textgrid.maxTime)

        for frequency_point in point_list:
            target_tier.addPoint(tg.Point(frequency_point.time.total_seconds(), frequency_point.label))
            frequency_tier.addPoint(tg.Point(frequency_point.time.total_seconds(), str(int(frequency_point.freq))))
        textgrid.append(target_tier)
        textgrid.append(frequency_tier)

        return textgrid


    @property
    def frequency_range(self):
        return self._frequency_range

    def downstep(self, scalar):
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)
