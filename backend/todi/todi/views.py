from django.http import HttpResponseRedirect
import subprocess
from django.contrib.auth.decorators import user_passes_test

def admin_check(user):
   return user.is_superuser

@user_passes_test(admin_check, login_url='/admin/login/?next=/rebuild-html/')
def rebuild_html(request):
    result = subprocess.run(["mdbook", "build", "--dest-dir", "../static"], cwd = "uploads")
    result.check_returncode()
    return HttpResponseRedirect('/static/page.html')
