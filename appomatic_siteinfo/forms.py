import haystack.forms
import django.forms
import haystack.fields
from haystack import connections
from haystack.constants import DEFAULT_ALIAS
import haystack.query


class SearchForm(haystack.forms.SearchForm):
    exclude = ['info', 'import_id', 'text', 'location']
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        connections[DEFAULT_ALIAS].get_unified_index().get_indexed_models()
        for model, index in connections[DEFAULT_ALIAS].get_unified_index().indexes.iteritems():
            for fieldname, field in index.fields.iteritems():
                if fieldname in self.exclude: continue
                verbose_name = fieldname
                try:
                    verbose_name = model._meta.get_field_by_name(field.model_attr)[0].verbose_name
                except:
                    pass
                if isinstance(field, haystack.fields.IntegerField):
                    self.fields["modelfield__%s__gte" % fieldname] = django.forms.IntegerField(required=False, label="%s (min)" % verbose_name)
                    self.fields["modelfield__%s__lte" % fieldname] = django.forms.IntegerField(required=False, label="%s (max)" % verbose_name)
                elif isinstance(field, haystack.fields.FloatField):
                    self.fields["modelfield__%s__gte" % fieldname] = django.forms.FloatField(required=False, label="%s (min)" % verbose_name)
                    self.fields["modelfield__%s__lte" % fieldname] = django.forms.FloatField(required=False, label="%s (max)" % verbose_name)
                elif isinstance(field, haystack.fields.DateTimeField):
                    self.fields["modelfield__%s__gte" % fieldname] = django.forms.DateTimeField(required=False, label="%s (min)" % verbose_name)
                    self.fields["modelfield__%s__lte" % fieldname] = django.forms.DateTimeField(required=False, label="%s (max)" % verbose_name)
                elif isinstance(field, haystack.fields.CharField):
                    self.fields["modelfield__%s" % fieldname] = django.forms.CharField(required=False, label=verbose_name)

    def search(self):
        sqs = super(SearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        filter = dict ((name[len("modelfield__"):], value)
                       for name, value in self.cleaned_data.iteritems()
                       if (name.startswith("modelfield__")
                           and value))

        if not len(sqs) and filter:
            sqs = haystack.query.SearchQuerySet()

        return sqs.filter(**filter)
