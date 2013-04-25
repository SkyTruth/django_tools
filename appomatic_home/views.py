import django.template
import django.shortcuts
import django.http
import django.db
import contextlib
import datetime
import math


def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_home/index.html',
        {},
        context_instance=django.template.RequestContext(request))
