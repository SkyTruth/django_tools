from django.conf.urls import *
from django.conf import settings
import django.views.generic

urlpatterns = patterns('',
    url(r'^alerts/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/index.html'), name="appomatic_alerts_index"),
    url(r'^alerts/subscribe/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/subscribe.html'), name="appomatic_alerts_subscribe"),
    url(r'^alerts/about/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/about.html'), name="appomatic_alerts_about"),
    url(r'^alerts/api/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/api.html'), name="appomatic_alerts_api"),
    url(r'^alerts/support/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/support.html'), name="appomatic_alerts_support"),
    url(r'^alerts/tags/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/tags.html'), name="appomatic_alerts_tags"),
    url(r'^alerts/sources/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_alerts/sources.html'), name="appomatic_alerts_sources"),
)
