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

        kwargs = {}
        if 'dp' in request.POST:
            kwargs['phrasal_downstep'] = float(request.POST['dp'])
        if 'da' in request.POST:
            kwargs['accentual_downstep'] = float(request.POST['da'])
        if 'FROMTIME' in request.POST:
            kwargs['from_time'] = float(request.POST['FROMTIME'])
        if 'TOTIME' in request.POST:
            kwargs['to_time'] = float(request.POST['TOTIME'])
        if 'STARTIME' in request.POST:
            kwargs['star_time'] = float(request.POST['STARTIME'])
        if 'Fr' in request.POST:
            kwargs['fr'] = float(request.POST['Fr'])
        if 'N' in request.POST:
            kwargs['n'] = float(request.POST['N'])
        if 'W' in request.POST:
            kwargs['w'] = float(request.POST['W'])

        sentence = json.loads(sentence)

        wav_path = os.path.realpath(os.path.join(static_directory, wav_filename))
        textgrid_path = os.path.realpath(os.path.join(static_directory, textgrid_filename))

        if os.path.commonpath([static_directory, wav_path, textgrid_path]) != static_directory:
            raise Exception

        (audio, img) = resynthesize(sentence, textgrid_path, wav_path, **kwargs)

        audio = base64.b64encode(audio).decode('ascii')
        img = img.decode('utf-8')

        retval = {'audio': audio, 'image': img}

        return HttpResponse(json.dumps(retval))

    #except Exception:
        #return HttpResponse('400: Bad request', status=400)
