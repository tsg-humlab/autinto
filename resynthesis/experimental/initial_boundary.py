from typing import Optional
from priv_types import ResynthPoint, IntonationalPhrase

class InitialBoundary:
    def __init__(self, accent: str, ip: IntonationalPhrase):
        assert accent in ['%L', '%H', '%HL', '!%L', '!%H', '!%HL']
        self.accent = accent
        self.ip = ip
        self.phrase = ip.phrase

    def decode(self) -> list[ResynthPoint]:
        self.phrasal_downstep()

        resynth_targets = []
        resynth_targets.append(self.first_target())
        second_target = self.second_target()
        if second_target is not None:
            resynth_targets.append(second_target)

        return resynth_targets

    def phrasal_downstep(self):
        (fr, n, w, dp) = (self.phrase.fr, self.phrase.n, self.phrase.w, self.phrase.phrasal_downstep)
        if self.accent.startswith('!'):
            self.freq_high = fr + dp*(n + w/2)
            self.freq_low  = fr + dp*(n - w/2)
        else:
            self.freq_high = fr + n + w/2
            self.freq_low  = fr + n - w/2

    # To create the first target of the initial boundary tone
    def first_target(self) -> ResynthPoint:
        time = self.ip.interval.start_time
        if self.accent in ['%L', '!%L']:
            label = 'LB1'
            freq  = self.freq_low + 0.3*self.phrase.w
        else:
            label = 'HB1'
            freq  = self.freq_high - 0.15*self.phrase.w

        return ResynthPoint(time, label, freq)


    # To create a second target, provided there is a minimal space
    # (here 100 ms) from the beginning of IP to the first pitch accent.
    def second_target(self) -> Optional[ResynthPoint]:
        time_to_accent_start = self.ip.voiced_portions[0].start_time - self.ip.interval.start_time
        if time_to_accent_start < 100:
            return None

        elif time_to_accent_start < 200:
            time = self.ip.interval.start_time + 0.5*time_to_accent_start
        else:
            time = self.ip.interval.start_time + time_to_accent_start - 100

        if self.accent in ['%H', '!H%']:
            label = 'HB2'
            freq  = self.freq_high - 0.3*self.phrase.w
        else:
            label = 'LB2'
            freq  = self.freq_low + 0.2*self.phrase.w
        
        return ResynthPoint(time, label, freq)
