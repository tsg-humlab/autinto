import subprocess

from . import sentence_parsing
from . import praatcall

def resynthesize(sentence, textgrid_file, audio_file, optional_args=None):
    new_textgrid = sentence_parsing.run(textgrid_file, sentence)
    (new_audio, pdf_image) = praatcall.send_to_praat(audio_file, new_textgrid)
    svg_image = pdf_to_svg(pdf_image)

    return (new_audio, svg_image)


def send_to_praat(audio_file, textgrid)
    pass


def pdf_to_svg(pdf_bytes):
    completed_process = subprocess.run(['pdftocairo', '-svg', '-', '-'], input=pdf_bytes, stdout=subprocess.PIPE)
    return completed_process.stdout
