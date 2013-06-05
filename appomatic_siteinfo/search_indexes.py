import datetime
import haystack.indexes
import appomatic_siteinfo.models


class EventIndex(haystack.indexes.ModelSearchIndex, haystack.indexes.Indexable):
    class Meta:
        model = appomatic_siteinfo.models.Event
