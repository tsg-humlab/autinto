from dataclasses import dataclass
from collections import deque

from resynthesis.phrase import Phrase, IntonationalPhrase
from resynthesis.pitch_accents import Word, InitialBoundary, FinalBoundary


@dataclass
class ResynthesizedIntonationalPhrase:
    initial_boundary: InitialBoundary
    words: list[Word]
    final_boundary: FinalBoundary

    def __init__(self, phrase_ip: IntonationalPhrase, sentence: deque[str]):
        str_initial_boundary = sentence.popleft()
        self.initial_boundary = InitialBoundary.from_name(str_initial_boundary,
                                                          self)

        self.words: list[Word] = []
        for voiced_portion in phrase_ip.vps:
            str_word = sentence.popleft()
            if str_word:
                word = Word.from_name(str_word,
                                      self,
                                      len(self.words),
                                      voiced_portion)
                self.words.append(word)

        str_final_boundary = sentence.popleft()
        self.final_boundary = FinalBoundary.from_name(str_final_boundary,
                                                      self)




@dataclass
class ResynthesizedPhrase:
    ips: list[ResynthesizedIntonationalPhrase]

    def __init__(self, phrase: Phrase, sentence: list[str]):
        self.ips: list[ResynthesizedIntonationalPhrase] = []

        sentence = deque(sentence)
        for phrase_ip in phrase.ips:
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence)
            self.ips.append(ip)
