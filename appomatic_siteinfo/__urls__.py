import django.conf.urls
import django.views.generic

urlpatterns = django.conf.urls.patterns('',
    django.conf.urls.url(r'^siteinfo/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_siteinfo/index.html'), name="appomatic_siteinfo_index"),
    django.conf.urls.url(r'^siteinfo/search/?$', 'appomatic_siteinfo.views.search'),
    django.conf.urls.url(r'^siteinfo/all/(?P<model>.*)/?$', 'appomatic_siteinfo.views.basemodel'),
    django.conf.urls.url(r'^siteinfo/clustersitelist/?$', 'appomatic_siteinfo.views.clustersitelist'),
    django.conf.urls.url(r'^siteinfo/(?P<guuid>.*)/?$', 'appomatic_siteinfo.views.basemodel'),
)
