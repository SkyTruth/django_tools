from django.conf.urls import *
from django.conf import settings
import django.views.generic

urlpatterns = patterns('',
    (r'^fracbot/check-records/?$', 'appomatic_fracbotserver.views.check_records'),
    (r'^fracbot/parse-pdf/?$', 'appomatic_fracbotserver.views.parse_pdf'),
    url(r'^fracbot/fracbot.user.js$', django.views.generic.TemplateView.as_view(template_name='appomatic_fracbotserver/fracbot.js', content_type="application/x-javascript; charset=UTF-8"), name="appomatic_fracbotserver_fracbot"),
)
