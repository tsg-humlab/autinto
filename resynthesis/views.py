import math
import datetime
import os
import json
import base64

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from . import resynthesize
from .types import Milliseconds

static_directory = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, 'static'))
assert os.path.isdir(static_directory), "ERROR: COULDN'T FIND STATIC DIRECTORY AT {}".format(static_directory)

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
            dp = float(request.POST['dp'])
            if not math.isnan(dp):
                kwargs['phrasal_downstep'] = dp
        if 'da' in request.POST:
            da = float(request.POST['da'])
            if not math.isnan(da):
                kwargs['accentual_downstep'] = da
        if 'FROMTIME' in request.POST:
            from_time = float(request.POST['FROMTIME'])
            if not math.isnan(from_time):
                kwargs['from_time'] = Milliseconds(from_time)
        if 'TOTIME' in request.POST:
            to_time = float(request.POST['TOTIME'])
            if not math.isnan(to_time):
                kwargs['to_time'] = Milliseconds(to_time)
        if 'STARTIME' in request.POST:
            star_time = float(request.POST['STARTIME'])
            if not math.isnan(star_time):
                kwargs['star_time'] = star_time
        if 'Fr' in request.POST:
            fr = float(request.POST['Fr'])
            if not math.isnan(fr):
                kwargs['fr'] = fr
        if 'N' in request.POST:
            n = float(request.POST['N'])
            if not math.isnan(n):
                kwargs['n'] = n
        if 'W' in request.POST:
            w = float(request.POST['W'])
            if not math.isnan(w):
                kwargs['w'] = w

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
