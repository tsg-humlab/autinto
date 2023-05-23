from resynthesis.phrase import Phrase
from resynthesis.resynthesized import ResynthesizedPhrase

def resynthesize(sentence, textgrid, audio, **kwargs):
    phrase = Phrase(textgrid)
    resynth_phrase = ResynthesizedPhrase(phrase, sentence)
    resynth_points = resynth_phrase.decode()
