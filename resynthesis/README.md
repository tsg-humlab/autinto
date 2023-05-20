# Transcription resynthesis

This Python package provides the resynthesis functionality to the ToDI server. The main functionality is
accessed through the ```resynthesize()``` function in [resynthesis.py](resynthesis.py), which takes a
list of [pitch accents](/frontend/book/src/0_about_this_course/0_3.md) (where '---' currently stands for
'no pitch accent'), a WAV file, and a previously prepared TextGrid, and returns the new wave file and an
image of the resynthesized audio.

To use this project, you will need to install the following things:
* [Praat](https://www.github.com/praat/praat); specifically, the ```praat``` executable must be available
  in the path variable. This project is currently being tested on Praat version 6.3.09.
* The ```pdftocairo``` tool needs to be available. This usually comes from the Poppler package of your
  distro.
* [textgrid](https://github.com/kylebgorman/textgrid), a Python library to read TextGrid files. Can be
  installed with ```pip install textgrid``` or [requirements.txt](requirements.txt).
* [TextGridTools](https://github.com/hbuschme/TextGridTools), which can be installed with ```pip install
  tgt```, but currently suffers from a deprecation issue that makes it **incompatible with Python 3.10 and
  up**.
  
  Currently, the best way to get around this seems to be to change the source code yourself. To do this,
  replace line 60 of tgt/core.py
```python
          if isinstance(tiers, collections.Sequence):
 ```
   with the updated:
```python
          if isinstance(tiers, collections.abc.Sequence):
 ```
 
   Alternatively, you can use [this fork](https://github.com/liasaki/TextGridTools/tree/master/tgt) of
   TextGridTools instead of getting the original from ```pip```.
