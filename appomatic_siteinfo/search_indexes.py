import datetime
import haystack.indexes
import appomatic_siteinfo.models


class EventIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Event

class SiteIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Site

class WellIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Well
