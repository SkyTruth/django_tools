import django.conf.urls
import django.views.generic

urlpatterns = django.conf.urls.patterns('',
    django.conf.urls.url(r'^siteinfo/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_siteinfo/index.html'), name="appomatic_siteinfo_index"),
    django.conf.urls.url(r'^operator/(?P<id>.*)/?$', 'appomatic_siteinfo.views.operator'),
    django.conf.urls.url(r'^site/(?P<id>.*)/?$', 'appomatic_siteinfo.views.site'),
    django.conf.urls.url(r'^well/(?P<id>.*)/?$', 'appomatic_siteinfo.views.well'),
    django.conf.urls.url(r'^event/(?P<id>.*)/?$', 'appomatic_siteinfo.views.event'),
)
