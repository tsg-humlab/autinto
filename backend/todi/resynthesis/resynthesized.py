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
        """ In this function, we create a ResynthesisedIntonationalPhrase,
         It consists of an initial boundary, all the words with a pitchaccent, and a final boundary """
        
        self.ip = phrase_ip
        self.parent = parent
        
        #Set the initial boundary and do extra processing for unaccented ip's
        str_initial_boundary = sentence.popleft()
        self.checkUnaccented(str_initial_boundary, sentence)
        self.initial_boundary = InitialBoundary(str_initial_boundary, self)
        

        

        #add all words with pitch accent to a list
        self.words: list[Word] = []
        for voiced_portion in phrase_ip.vps:
            str_word = sentence.popleft()
            if str_word:
                word = Word(str_word,
                            self,
                            len(self.words),
                            voiced_portion)
                self.words.append(word)
        
        #Set the final boundary.
        str_final_boundary = sentence.popleft()
        self.final_boundary = FinalBoundary(str_final_boundary, self)

        # We only set this when the decoding starts
        self._frequency_range = None

    def decode(self, point_list):
        # Reset frequency_range
        self.reset_downstep()

        #decode all pitch accents in the ResynthesisedIntonationalPhrase. 
        #decode explained in pitch_accents.py for each class initial_boundary, word and final_boundary
        self.initial_boundary.decode(point_list)
        for word in self.words:
            word.decode(point_list)
        self.final_boundary.decode(point_list)

        self.parent._frequency_range = self.frequency_range

    #these @property defenitions are used to more easily retrieve properties from a previous type within this class.
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

    #apply the frequency scaling for a downstep.
    def downstep(self, scalar):
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)

    #reset downstep
    def reset_downstep(self):
        self._frequency_range = None
    
    #Check if there is a unaccented ip, if this is the case, we set it as an initial boundary and add an empty word
    #to keep our vp indexing consistent.
    def checkUnaccented(self, str_initial_boundary, sentence):
        if str_initial_boundary in {"H", "L"}:
            sentence.insert(0, None)


@dataclass
class ResynthesizedPhrase:
    textgrid: tg.TextGrid
    ips:  list[ResynthesizedIntonationalPhrase]
    vars: ResynthesizeVariables

    def __init__(self, phrase: Phrase, sentence: list[str], **kwargs):
        """We recieve a list of Those parameters that the student has changed, Here we check
        which values have been declared and which have not, those left empty are updated
        with the default values"""

        self.ips: list[ResynthesizedIntonationalPhrase] = []
        self.textgrid = phrase.textgrid

        #check the gender and set default values accordingly
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

        #set remaining default values if neccessary.
        self.vars = ResynthesizeVariables(**kwargs)

        sentence = deque(sentence)
        for phrase_ip in phrase.ips:
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence, self)
            self.ips.append(ip)

        #Set the initial frequencies
        freq_low = self.vars.fr + self.vars.n - 0.5*self.vars.w
        freq_high = self.vars.fr + self.vars.n + 0.5*self.vars.w
        self._frequency_range = FrequencyRange(freq_low, freq_high)


    
    def decode(self):
        """
        decode all ResynthesizedIntonationalPhrase, by looping through each of them and calling their own decode function on it.
        """
        point_list = []
        for ip in self.ips:

            #Decode each ResynthesizedIntonationalPhrase
            ip.decode(point_list)
        return point_list


    def decode_into_textgrid(self):
        """
        Add the word_tier, target_tier and frequency_tiers to the textgrid with their correct corresponding targetlabels, timings and frequency.
        """
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

        #create tier objects.
        target_tier = tg.PointTier('targets', self.textgrid.minTime, self.textgrid.maxTime)
        frequency_tier = tg.PointTier('ToDI-F0', self.textgrid.minTime, self.textgrid.maxTime)

        #add the newly generated frequency_points to the target_tier and frequency_tier
        for frequency_point in point_list:
            target_tier.addPoint(tg.Point(frequency_point.time.total_seconds(), frequency_point.label))
            frequency_tier.addPoint(tg.Point(frequency_point.time.total_seconds(), str(int(frequency_point.freq))))
        
        #add tier to textgrid
        textgrid.append(target_tier)
        textgrid.append(frequency_tier)

        return textgrid


    @property
    def frequency_range(self):
        return self._frequency_range

    #Set the frequency values to the downstepped values.
    def downstep(self, scalar):
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)
