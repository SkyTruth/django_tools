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
        src = appomatic_siteinfo.models.Source.get("FracFocus", "")

        for idx, scrape in enumerate(appomatic_legacymodels.models.Fracfocusscrape.objects.filter(seqid__gt = src.import_id).order_by("seqid")):

            report = appomatic_legacymodels.models.Fracfocusreport.objects.filter(pdf_seqid = scrape.seqid)[0] # Don't use get, there are duplicates!

            print "%s @ %s" % (scrape.api, scrape.job_date)

            operator = appomatic_siteinfo.models.Company.get(scrape.operator)

            # Format: SS-CCC-NNNNN-XX-XX
            api = scrape.api.split("-")
            while len(api) < 5:
                api.append('00')
            if len(api) != 5 or len(api[0]) != 2 or len(api[1]) != 3 or len(api[2]) != 5 or len(api[3]) != 2 or len(api[4]) != 2:
                print "    Ignoring broken api: %s" % (scrape.api,)
                continue
            api = '-'.join(api)

            well = appomatic_siteinfo.models.Well.get(api, scrape.well_name, scrape.latitude, scrape.longitude, conventional = False)

            info = dict((name, getattr(scrape, name))
                        for name in appomatic_legacymodels.models.Fracfocusscrape._meta.get_all_field_names())
            info.update(dict((name, getattr(report, name))
                             for name in appomatic_legacymodels.models.Fracfocusreport._meta.get_all_field_names()))

            event = appomatic_siteinfo.models.FracEvent(
                src = src,
                import_id = scrape.seqid,
                latitude = scrape.latitude,
                longitude = scrape.longitude,
                datetime = datetime.datetime(report.fracture_date.year, report.fracture_date.month, report.fracture_date.day).replace(tzinfo=pytz.utc),
                site = well.site,
                well = well,
                operator = operator,
                true_vertical_depth = report.true_vertical_depth,
                total_water_volume = report.total_water_volume,
                published = report.published.replace(tzinfo=pytz.utc),
                infourl = None,
                info = info
                )
            event.save()


            for reportchemical in appomatic_legacymodels.models.Fracfocusreportchemical.objects.filter(pdf_seqid=scrape.seqid):
                print "    %s" % (reportchemical.trade_name or reportchemical.ingredients or reportchemical.cas_number,)

                info = dict((name, getattr(reportchemical, name))
                            for name in appomatic_legacymodels.models.Fracfocusreportchemical._meta.get_all_field_names())

                chemical = appomatic_siteinfo.models.Chemical.get(
                    trade_name = reportchemical.trade_name,
                    ingredients = reportchemical.ingredients,
                    cas_type = reportchemical.cas_type,
                    cas_number = reportchemical.cas_number,
                    comments = reportchemical.comments)
                               
                appomatic_siteinfo.models.ChemicalUsageEventChemical(
                    event = event,
                    chemical = chemical,
                    supplier = appomatic_siteinfo.models.Company.get(reportchemical.supplier),
                    purpose = appomatic_siteinfo.models.ChemicalPurpose.get(reportchemical.purpose),
                    additive_concentration = reportchemical.additive_concentration,
                    weight = reportchemical.weight,
                    ingredient_weight = reportchemical.ingredient_weight,
                    hf_fluid_concentration = reportchemical.hf_fluid_concentration,
                    info = info).save()

            src.import_id = scrape.seqid
            src.save()

            if idx % 50 == 0:
                django.db.transaction.commit()
                django.db.reset_queries()
        django.db.transaction.commit()
