import subprocess
import os
import time
from sys import stderr

import textgrid

from . import sentence_parsing

def resynthesize(sentence, textgrid_file, audio_file, optional_args=None):
    new_textgrid = sentence_parsing.run(textgrid_file, sentence)

    (new_audio, pdf_image) = send_to_praat(audio_file, new_textgrid)
    svg_image = pdf_to_svg(pdf_image)

    return (new_audio, svg_image)


def send_to_praat(audio_file, textgrid):
    prefix = make_pipes()

    resynthesis_dir = os.path.dirname(__file__)
    praat_script = os.path.join(resynthesis_dir, 'resynth.praat')

    #Praat won't accept input as a pipe, so we make a temp file for the TextGrid
    textgrid.write('{}.TextGrid'.format(prefix))
    
    praat_exec = subprocess.Popen(['praat', '--run', praat_script, audio_file, prefix+'.TextGrid', prefix+'.wav', prefix+'.pdf'])



    praat_exec.wait(timeout=10)

    wav_pipe = open(prefix+'.wav', 'rb', buffering=500_000)
    pdf_pipe = open(prefix+'.pdf', 'rb', buffering=500_000)


    wav_out = wav_pipe.read()
    wav_pipe.close()
    pdf_out = pdf_pipe.read()
    pdf_pipe.close()

    assert(len(wav_out) < 500_000)
    assert(len(pdf_out) < 500_000)

    cleanup_pipes(prefix)
    os.unlink('{}.TextGrid'.format(prefix))

    return wav_out, pdf_out


def pdf_to_svg(pdf_bytes):
    completed_process = subprocess.run(['pdftocairo', '-svg', '-', '-'], input=pdf_bytes, stdout=subprocess.PIPE)
    return completed_process.stdout



suffixes = ['wav', 'pdf'] #, 'TextGrid']
def make_pipes():
    tmp_prefix = '/tmp/todi-resynth-{}'.format(time.time_ns())
    #for suffix in suffixes:
        #os.mkfifo('{}.{}'.format(tmp_prefix, suffix))
    return tmp_prefix

def cleanup_pipes(prefix: str):
    for suffix in suffixes:
        try:
            os.unlink('{}.{}'.format(prefix, suffix))
        except FileNotFoundError:
            print('Error: Tried to unlink non-existing pipes.', file=stderr)
