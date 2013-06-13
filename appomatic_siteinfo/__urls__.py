import django.conf.urls
import django.views.generic
import haystack.views
import haystack.forms
import appomatic_siteinfo.forms

urlpatterns = django.conf.urls.patterns('',
    django.conf.urls.url(r'^siteinfo/?$', django.views.generic.TemplateView.as_view(template_name='appomatic_siteinfo/index.html'), name="appomatic_siteinfo_index"),
    django.conf.urls.url(r'^siteinfo/search/?', haystack.views.search_view_factory(form_class=appomatic_siteinfo.forms.SearchForm, template="appomatic_siteinfo/search.html"), name='appomatic_siteinfo_search'),
    django.conf.urls.url(r'^siteinfo/(?P<id>.*)/?$', 'appomatic_siteinfo.views.basemodel'),
)
