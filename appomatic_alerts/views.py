import django.template
import django.shortcuts
import django.http
import django.template
import django.shortcuts
import django.http

def index(request):
    return django.shortcuts.render_to_response(
        'appomatic_alerts/index.html',
        {},
        context_instance=django.template.RequestContext(request))

def subscribe(request):
    return django.shortcuts.render_to_response(
        'appomatic_alerts/subscribe.html',
        {},
        context_instance=django.template.RequestContext(request))

def about(request):
    return django.shortcuts.render_to_response(
        'appomatic_alerts/about.html',
        {},
        context_instance=django.template.RequestContext(request))

def api(request):
    return django.shortcuts.render_to_response(
        'appomatic_alerts/api.html',
        {},
        context_instance=django.template.RequestContext(request))

def support(request):
    return django.shortcuts.render_to_response(
        'appomatic_alerts/support.html',
        {},
        context_instance=django.template.RequestContext(request))
