from django.http import HttpResponse
import subprocess


def rebuild_html(request):
    result = subprocess.run(["mdbook", "build", "--dest-dir", "../static"], cwd = "uploads")
    result.check_returncode()
    return HttpResponse()