import subprocess
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/admin/login/?next=/rebuild-html')
def rebuild_html(request):
        result = subprocess.run(["mdbook", "build", "--dest-dir", "../static"], cwd = "uploads")
        result.check_returncode()
        return render(request, "rebuild_success.html")
