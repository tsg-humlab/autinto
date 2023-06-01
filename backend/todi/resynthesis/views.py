import os
import json
import base64

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from . import resynthesize

static_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, 'static'))
assert os.path.isdir(static_directory), "ERROR: COULDN'T FIND STATIC DIRECTORY"

@csrf_exempt
def handle(request):
    #try:
        if request.method != "POST":
            return HttpResponse('400: Bad request', status=400)

        sentence = request.POST['sentence']
        wav_filename = request.POST['wav']
        textgrid_filename = request.POST['TextGrid']

        sentence = json.loads(sentence)
        for (i,item) in enumerate(sentence):
            if item is None:
                sentence[i] = '---'

        wav_path = os.path.realpath(os.path.join(static_directory, wav_filename))
        textgrid_path = os.path.realpath(os.path.join(static_directory, textgrid_filename))

        if os.path.commonpath([static_directory, wav_path, textgrid_path]) != static_directory:
            raise Exception

        (audio, img) = resynthesize(sentence, textgrid_path, wav_path)

        audio = str(base64.b64encode(audio))
        img = str(img)

        retval = {'audio': audio, 'image': img}

        return HttpResponse(json.dumps(retval))

    #except Exception:
        #return HttpResponse('400: Bad request', status=400)
