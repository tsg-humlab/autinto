from typing import Optional
from priv_types import ResynthPoint, IntonationalPhrase

class FinalBoundary:
    def __init__(self, accent: str, ip: IntonationalPhrase):
        assert accent in ['L%', 'H%', '%']
        self.accent = accent
        self.ip = ip
        self.phrase = ip.phrase

    def decode(self) -> ResynthPoint:
        ip_end = self.ip.interval.end_time
        match self.accent:
            case 'L%':
                return ResynthPoint(time=ip_end, label='LE', freq=self.ip.freq_low)
            case 'H%':
                return ResynthPoint(time=ip_end, label='HE', freq=self.ip.freq_high)
            case '%':
                last_word = self.ip.voiced_portions[-1]
                match last_word:
                    case 'H*L'|'!H*L'|'L*HL'|'L*!HL':
                        freq = self.ip.freq_low + 0.4*self.ip.w
                    case 'H*'|'L*H':
                        freq = self.ip.freq_high - 0.4*self.ip.w
                    case 'L*':
                        freq = self.ip.freq_low - 0.2*w
                    case '!H*'|'H*LH':
                        raise NotImplementedError
                    case _:
                        raise ValueError

                return ResynthPoint(time=ip_end, label='ME', freq=freq)
