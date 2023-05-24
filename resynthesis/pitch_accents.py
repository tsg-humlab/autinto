from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re

from resynthesis.types import Milliseconds, FrequencyPoint
from resynthesis.abstract_pitch_accents import AbstractWord, AbstractInitialBoundary, AbstractFinalBoundary

class Tone(Enum):
    HIGH = 1
    LOW  = 2

    @staticmethod
    def from_name(name: str):
        match name:
            case 'L':
                return Tone.LOW
            case 'H':
                return Tone.HIGH
            case '!H':
                # TODO Downstep
                return Tone.HIGH


class Word(AbstractWord):
    primary_tone: Tone
    middle_tone:  Optional[Tone] = None
    final_tone:   Optional[Tone] = None

    def decode(self, point_list):
        self.decode_primary(point_list)
        self.decode_middle(point_list)
        self.decode_final(point_list)


    def decode_primary(self, point_list):
        match self.primary_tone:
            case Tone.LOW:
                self.decode_primary_low(point_list)
            case Tone.HIGH:
                self.decode_primary_high(point_list)

    def decode_primary_low(self, point_list):
        # LOW TRAY FOR L*, PLUS DELAYED PEAK
        # This rule creates an extended dip for L*.

        # Point L1 always comes just before the VP. Points L2 and L3 are
        # placed depending on the amount of time available after the
        # current VP.

        # If there is enough time, the VP range plus 360 milliseconds is
        # used:
        if self.time_to_next_boundary > Milliseconds(360):
            delayspace = self.vp_duration + Milliseconds(360)
            time_L2 = self.vp_start + 0.05 * delayspace
            time_L3 = self.vp_start + 0.70 * delayspace
        # Otherwise, if there is a boundary (either the IP ends or the
        # next VP starts) within 360 milliseconds, L2 and L3 are placed
        # earlier:
        else:
            delayspace = self.vp_duration + self.time_to_next_boundary
            time_L2 = self.vp_start + 0.03 * delayspace
            time_L3 = self.vp_start + 0.26 * delayspace

        # TODO comment here
        point_L1 = FrequencyPoint(
            label = 'L1',
            freq  = self.scale_frequency(0.2),
            time  = self.vp_start - Milliseconds(10))
        point_L2 = FrequencyPoint(
            label = 'L2',
            freq  = self.scale_frequency(0.15),
            time  = time_L2)
        point_L3 = FrequencyPoint(
            label = 'L3',
            freq  = self.scale_frequency(0.15),
            time  = time_L3)

        point_list.append(point_L1)
        point_list.append(point_L2)
        point_list.append(point_L3)

    def decode_primary_high(self, point_list):
        # FLAT-TOP PEAK
        # This rule creates the first and second targets of H* in its
        # VP.

        if self.vp_duration < Milliseconds(250):
            time_H1 = self.vp_start + 0.12 * self.vp_duration
            time_H2 = self.vp_start + 0.42 * self.vp_duration
        else:
            time_H1 = self.vp_start + 0.30 * self.vp_duration
            time_H2 = self.vp_start + 0.60 * self.vp_duration

        point_H1 = FrequencyPoint(
            label = 'H1',
            freq  = self.scale_frequency(0.7),
            time  = time_H1)
        point_H2 = FrequencyPoint(
            label = 'H2',
            freq  = self.scale_frequency(0.7),
            time  = time_H2)

        point_list.append(point_H1)
        point_list.append(point_H2)


    def decode_middle(self, point_list):
        match self.middle_tone:
            case None:
                return
            case Tone.HIGH:
                self.decode_middle_high(point_list)
            case Tone.LOW:
                self.decode_middle_low(point_list)
    
    def decode_middle_high(self, point_list):
        raise NotImplementedError

    def decode_middle_low(self, point_list):
        raise NotImplementedError


    def decode_final(self, point_list):
        if self.final_tone is None:
            return
        else:
            raise NotImplementedError


    def from_name(self, name: str):
       result = re.findall(r'!?[HL]\*?', name)
       # ^ 'L*!HL returns ['L*', '!H', 'L']

       self.primary_tone = Tone.from_name(result[0][:-1])
       self.final_tone   = Tone.from_name(result[-1]) if len(result) > 1 else None
       self.middle_tone  = Tone.from_name(result[1])  if len(result) > 2 else None


class InitialBoundary(AbstractInitialBoundary):
    name: str

    def decode(self):
        raise NotImplementedError

    def from_name(self, name: str):
        self.name = name


class FinalBoundary(AbstractFinalBoundary):
    name: str

    def decode(self):
        raise NotImplementedError

    def from_name(self, name: str):
        self.name = name
