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

    def decode_middle(self, point_list):
        match self.middle_tone:
            case None:
                return
            case Tone.HIGH:
                self.decode_middle_high(point_list)
            case Tone.LOW:
                self.decode_middle_low(point_list)

    def decode_final(self, point_list):
        match self.final_tone:
            case None:
                return
            case Tone.LOW:
                self.decode_final_low(point_list)
            case Tone.HIGH:
                self.decode_final_high(point_list)
    

    def decode_primary_low(self, point_list):
        # LOW TRAY FOR L*, PLUS DELAYED PEAK
        # This rule creates an extended dip for L*.

        # Point L1 always comes just before the VP. Points L2 and L3 are
        # placed depending on the amount of time available after the
        # current VP.

        # If there is enough time, L2 and L3 are placed in the VP
        # directly:
        if self.time_to_next_boundary > Milliseconds(360):
            time_L2 = self.vp_start + 0.05 * self.vp_duration
            time_L3 = self.vp_start + 0.75 * self.vp_duration
        # Otherwise, if there is a boundary (either the IP ends or the
        # next VP starts) within 360 milliseconds, the available space
        # is calculated, and L2 and L3 are placed depending on that:
        else:
            time_L2 = self.vp_start + 0.03 * self.delayspace
            time_L3 = self.vp_start + 0.30 * self.delayspace

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


    def decode_middle_high(self, point_list):
        #LOW TRAY FOR L*, PLUS DELAYED PEAK
        # This rule creates a delayed peak after L*

        # TODO downstep

        if self.time_to_next_boundary > Milliseconds(360):
            # Since there is enough space, the last point, L3, has been
            # placed at 0.75 into the VP.
            last_point_time = self.vp_start + 0.75*self.vp_duration

            time_H1 = last_point_time + 0.5 * self.delayspace
            time_H2 = last_point_time + 0.7 * self.delayspace
        else:
            time_H1 = self.vp_start + 0.60 * self.delayspace
            time_H2 = self.vp_start + 0.70 * self.delayspace



        point_H1 = FrequencyPoint(
            label = 'H1',
            freq  = self.scale_frequency(0.70),
            time  = time_H1)
        point_H2 = FrequencyPoint(
            label = 'H2',
            freq  = self.scale_frequency(0.70),
            time  = time_H2)

        point_list.append(point_H1)
        point_list.append(point_H2)



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


    def decode_middle_low(self, point_list):        
        # PRENUCLEAR RISE AND FALL-RISE
        # This rule creates  the fall from H* in H*LH.

        last_target_time = point_list[-1].time
        if self.next_boundary - last_target_time < Milliseconds(200):
            time_l = last_target_time + 0.30 * (self.next_vp_start - last_target_time)
        else:
            time_l = last_target_time + Millisecoonds(100)


        point_l = FrequencyPoint(
            label = '+l',
            freq  = self.scale_frequency(0.4),
            time  = time_l)
        
        point_list.append(point_l)


    def decode_final_low(self, point_list):
        if not self.is_last_word:
            self.decode_pre_nuclear_fall(point_list)
        else:
            self.decode_nuclear_fall(point_list)

    def decode_pre_nuclear_fall(self, point_list):
        # PRE-NUCLEAR FALL
        # This rule creates a slow fall before another toneword.

        if self.time_to_next_word < Milliseconds(200):
            time = self.vp_end + 0.5*self.time_to_next_word
            freq = self.scale_frequency(0.40)
        else:
            time = self.vp_end + self.time_to_next_word - Milliseconds(100)
            freq = self.scale_frequency(0.25)

        point_l1 = FrequencyPoint(
            label = 'l1',
            freq = freq,
            time = time)

        point_list.append(point_l1)

    def decode_nuclear_fall(self, point_list):
        # NUCLEAR FALL
        # This rule creates a fast nuclear fall after (!)H*L and
        # (!)L*HL.

        # If the final boundary is %, no points are created, and the
        # method returns early.
        if self.final_boundary == '%':
            return

        # Otherwise, if there is not much time, only one point is
        # created. We make a variable here to store whether the second
        # point needs to be made:
        make_l2 = False

        time_preceding_target = point_list[-1].time
        spread_space = self.ip_end - time_preceding_target
        if spread_space < Milliseconds(220):
            time_l1 = time_preceding_target + 0.5*spread_space
        else:
            time_l1 = time_preceding_target + Milliseconds(100)
            time_l2 = self.ip_end - Milliseconds(100)
            make_l2 = True

        point_l1 = FrequencyPoint(
            label = 'l1',
            freq = self.scale_frequency(0.15),
            time = time_l1)
        point_list.append(point_l1)

        if make_l2:
            point_l2 = FrequencyPoint(
                label = 'l2',
                freq = self.scale_frequency(0.15),
                time = time_l2)
            point_list.append(point_l2)


    def decode_final_high(self, point_list):
        time_preceding_target = point_list[-1].time
        if get_Tvpbegin(next_word) - time_preceding_target < FROMTIME * 2:
            htime = time_preceding_target + get_time(next_word) - time_preceding_target * 0.5
        else:
            htime = get_time(next_word) - TOTIME

        point_h1 = FrequencyPoint(
            label = 'h1',
            freq  = freq_high - 0.3 * W,
            time  = htime)

        point_list.append(point_+l)


    def from_name(self, name: str):
       result = re.findall(r'!?[HL]\*?', name)
       # ^ 'L*!HL returns ['L*', '!H', 'L']

       self.primary_tone = Tone.from_name(result[0][:-1])
       self.final_tone   = Tone.from_name(result[-1]) if len(result) > 1 else None
       self.middle_tone  = Tone.from_name(result[1])  if len(result) > 2 else None


class InitialBoundary(AbstractInitialBoundary):
    first_target_tone: Tone
    second_target_tone: Tone

    def decode(self, point_list):
        self.decode_first_target(point_list)
        self.decode_second_target(point_list)

    def decode_first_target(self, point_list):
        match self.first_target_tone:
            case Tone.LOW:
                label = 'LB1'
                freq = self.scale_frequency(0.30)
            case Tone.HIGH:
                label = 'HB1'
                freq = self.scale_frequency(0.85)

        first_target = FrequencyPoint(
            label = label,
            freq  = freq,
            time  = self.ip_start)

        point_list.append(first_target)

    def decode_second_target(self, point_list):
        # If there are less than 100 milliseconds before the first word,
        # then no second target is created, and the function returns
        # early.
        if self.time_to_first_word < Milliseconds(100):
            return

        # Otherwise, if there are less than 200 milliseconds, the second
        # target is placed halfway between the IP start and the first
        # word.
        elif self.time_to_first_word < Milliseconds(200):
            time = self.ip_start + 0.5*self.time_to_first_word
        # Otherwise, if there are more than 200 milliseconds, the second
        # target is placed 100 milliseconds before the first word.
        else:
            time = self.ip_start + self.time_to_first_word - Milliseconds(100)

        match self.second_target_tone:
            case Tone.LOW:
                label = 'LB2'
                freq = self.scale_frequency(0.20)
            case Tone.HIGH:
                label = 'HB2'
                freq = self.scale_frequency(0.70)

        second_target = FrequencyPoint(
            label = label,
            freq = freq,
            time = time)

        point_list.append(second_target)
        


    def from_name(self, name: str):
        if name not in ['%L', '%H', '%HL', '!%L', '!%H', '!%HL']:
            raise ValueError

        if name[0] == '!':
            # TODO downstep
            name = name[1:]

        self.first_target_tone = Tone.from_name(name[1])
        self.second_target_tone = Tone.from_name(name[-1])

class FinalBoundary(AbstractFinalBoundary):
    tone: Optional[Tone]

    def decode(self, point_list):
        self.decode_nuclear_rise_and_spread(point_list)
        self.decode_final_boundary(point_list)

    def decode_nuclear_rise_and_spread(self, point_list):
        match self.last_word:
            case 'L%':
                raise NotImplementedError
            case 'H*' | '!H*':
                raise NotImplementedError
            case 'L*H':
                raise NotImplementedError
            case _:
                pass

    def decode_final_boundary(self, point_list):
        match self.name:
            case 'L%':
                label = 'LE'
                freq = self.scale_frequency(0.0)
            case 'H%':
                label = 'HE'
                freq = self.scale_frequency(1.0) # TODO handle downstep
            case '%':
                raise NotImplementedError


    def from_name(self, name: str):
        # The final boundary is so simple that we can simply use
        # self.name in the main logic.
        if name not in ['L%', 'H%', '%']:
            raise ValueError
        pass
