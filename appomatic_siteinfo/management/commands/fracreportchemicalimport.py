import django.core.management.base
import appomatic_siteinfo.models
import appomatic_legacymodels.models
import optparse
import contextlib
import datetime
import sys
import os.path
import logging
import csv
import django.contrib.gis.geos
from django.conf import settings 
import django.db.transaction
import pytz

class Command(django.core.management.base.BaseCommand):

    @django.db.transaction.commit_manually
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
        src = appomatic_siteinfo.models.Source.get("FracFocus", "ReportChemical")

        for idx, row in enumerate(appomatic_legacymodels.models.Fracfocusreportchemical.objects.filter(seqid__gt = src.import_id).order_by("seqid")):

            print "%s: %s" % (row.api, row.trade_name or row.ingredients or row.cas_number)

            info = dict((name, getattr(row, name))
                        for name in appomatic_legacymodels.models.Fracfocusreportchemical._meta.get_all_field_names())

            appomatic_siteinfo.models.ChemicalUsageEventChemical(
                event = appomatic_siteinfo.models.FracEvent.objects.get(import_id = row.pdf_seqid),    
                chemical = appomatic_siteinfo.models.Chemical.get(trade_name = row.trade_name, ingredients = row.ingredients, cas_type = row.cas_type, cas_number = row.cas_number, comments = row.comments),
                supplier = appomatic_siteinfo.models.Supplier.get(row.supplier),
                purpose = appomatic_siteinfo.models.ChemicalPurpose.get(row.purpose),
                additive_concentration = row.additive_concentration,
                weight = row.weight,
                ingredient_weight = row.ingredient_weight,
                hf_fluid_concentration = row.hf_fluid_concentration,
                info = info).save()

            src.import_id = row.seqid
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
        django.db.transaction.commit()
