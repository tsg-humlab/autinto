from dataclasses import dataclass

import tgt
from tgt.core import TextGrid, IntervalTier

Milliseconds = int

@dataclass
class Interval:
    start_time: Milliseconds
    end_time:   Milliseconds

    def __init__(self, start_time: float, end_time: float):
        self.start_time = Milliseconds(start_time*1000)
        self.end_time = Milliseconds(end_time*1000)

@dataclass
class VoicedPortion(Interval):
    def __init__(self, start_time, end_time):
        super().__init__(start_time, end_time)


@dataclass
class IntonationalPhrase(Interval):
    vps: list[VoicedPortion]

    def __init__(self, start_time, end_time, textgrid_vps: IntervalTier):
        super().__init__(start_time, end_time)

        self.vps: list[VoicedPortion] = []

        for textgrid_vp in textgrid_vps:
            vp = VoicedPortion(textgrid_vp.start_time, textgrid_vp.end_time)
            if (vp.start_time > self.start_time
                    and vp.end_time < self.end_time):
                self.vps.append(vp)
                


@dataclass
class Phrase(Interval):
    ips: list[IntonationalPhrase]

    def __init__(self, textgrid: str):
        textgrid = tgt.read_textgrid(textgrid)
        super().__init__(textgrid.start_time, textgrid.end_time)

        textgrid_ips = textgrid.get_tier_by_name("IP's")
        textgrid_vps = textgrid.get_tier_by_name('vp')

        self.ips: list[IntonationalPhrase] = []

        for textgrid_ip in textgrid_ips:
            ip = IntonationalPhrase(textgrid_ip.start_time, textgrid_ip.end_time, textgrid_vps)
            self.ips.append(ip)
