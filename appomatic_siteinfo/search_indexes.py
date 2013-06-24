import datetime
import haystack.indexes
import appomatic_siteinfo.models

class CompanyIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Company

class SiteIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Site

class WellIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Well

class ChemicalPurposeIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.ChemicalPurpose

class ChemicalPurposeIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.ChemicalPurpose

class ChemicalIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Chemical

class EventIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Event

