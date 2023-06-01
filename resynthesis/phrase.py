from dataclasses import dataclass
import textgrid as tg

from resynthesis.types import Milliseconds, Interval

@dataclass
class VoicedPortion(Interval):
    def __init__(self, start_time, end_time):
        super().__init__(start_time, end_time)


@dataclass
class IntonationalPhrase(Interval):
    vps: list[VoicedPortion]

    def __init__(self, start_time, end_time, textgrid_vps):
        super().__init__(start_time, end_time)

        self.vps: list[VoicedPortion] = []

        for textgrid_vp in textgrid_vps:
            vp = VoicedPortion(textgrid_vp.minTime, textgrid_vp.maxTime)
            if (vp.start_time > self.start_time
                    and vp.end_time < self.end_time):
                self.vps.append(vp)
                


@dataclass
class Phrase(Interval):
    ips: list[IntonationalPhrase]

    def __init__(self, file: str):
        textgrid = tg.TextGrid.fromFile(file) 
        super().__init__(textgrid.minTime, textgrid.maxTime)

        textgrid_ips = textgrid.getFirst("IP's")
        textgrid_vps = textgrid.getFirst('vp')

        self.ips: list[IntonationalPhrase] = []
        for textgrid_ip in textgrid_ips:
            ip = IntonationalPhrase(textgrid_ip.minTime, textgrid_ip.maxTime, textgrid_vps)
            self.ips.append(ip)
