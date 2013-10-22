from django.conf.urls import *
from django.conf import settings
import django.views.generic

urlpatterns = patterns('',
    (r'^fracbot/client-log/?$', 'appomatic_fracbotserver.views.client_log'),
    (r'^fracbot/update-states/?$', 'appomatic_fracbotserver.views.update_states'),
    (r'^fracbot/update-counties/?$', 'appomatic_fracbotserver.views.update_counties'),
    (r'^fracbot/check-records/?$', 'appomatic_fracbotserver.views.check_records'),
    (r'^fracbot/parse-pdf/?$', 'appomatic_fracbotserver.views.parse_pdf'),
    url(r'^fracbot/fracbot.user.js$', django.views.generic.TemplateView.as_view(template_name='appomatic_fracbotserver/fracbot.js', content_type="application/x-javascript; charset=UTF-8"), name="appomatic_fracbotserver_fracbot"),
    (r'^fracbot/task/?$', 'appomatic_fracbotserver.views.get_task'),
    (r'^admin/appomatic_fracbotserver/statistics/?$', 'appomatic_fracbotserver.views.statistics'),
    (r'^admin/appomatic_fracbotserver/statistics/data/?$', 'appomatic_fracbotserver.views.statistics_data'),
)
