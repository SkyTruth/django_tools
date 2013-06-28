import datetime
import haystack.indexes
import appomatic_siteinfo.models

class CompanyIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Company
    model_type = haystack.indexes.CharField(model_attr='type_name')

class SiteIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Site
    model_type = haystack.indexes.CharField(model_attr='type_name')

class WellIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Well
    model_type = haystack.indexes.CharField(model_attr='type_name')

class ChemicalPurposeIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.ChemicalPurpose
    model_type = haystack.indexes.CharField(model_attr='type_name')

class ChemicalPurposeIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.ChemicalPurpose
    model_type = haystack.indexes.CharField(model_attr='type_name')

class ChemicalIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Chemical
    model_type = haystack.indexes.CharField(model_attr='type_name')

class EventIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Event
    model_type = haystack.indexes.CharField(model_attr='type_name')

