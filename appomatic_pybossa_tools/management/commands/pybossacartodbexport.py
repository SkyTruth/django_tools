import django.core.management.base
import appomatic_pybossa_tools.models
import optparse
import contextlib
import datetime
import sys
import os.path
import logging
from django.conf import settings 
import django.db.transaction
import pytz
import cartodb

class Command(django.core.management.base.BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            return self.handle2(*args, **kwargs)
        except Exception, e:
            print e
            import traceback
            traceback.print_exc()

    def handle2(self, *args, **kwargs):
	cc = cartodb.CartoDBAPIKey("70674365b3e4c76997fe825a4993200ce3cb480a", "redhog")

       	counties = {}

	for task in appomatic_pybossa_tools.models.Task.objects.filter(app__name="frackfinder_tadpole"):
            county = task.info['info']['county']
            if county not in counties:
                counties[county] = {'total': 0, 'done': 0, 'name': county}
            counties[county]['total'] += task.info['n_answers']
            counties[county]['done'] += task.answers.count()
	    print "x"

        cc.sql("delete from tadpole")
        for county in counties.itervalues():
            cc.sql("insert into tadpole(county, done, total) values ('%(name)s', '%(done)s', '%(total)s')" % county)
            print "."

	#Lastid = cc.sql("select max(lastid) lastid from tadpole")['rows'][0]['lastid']

        #for idx, answer in enumerate(appomatic_pybossa_tools.models.Answer.objects.filter(task__app__name="frackfinder_tadpole", id__gt = lastid).order_by("id")):
        #    existing = cc.sql("select count(*) count from tadpole where county = '%s' and site = '%s'" % (
        #        answer.task.info['info']['county'],
        #        answer.task.info['info']['siteID'];
        #        ))['rows'][0]['count']
        #    if existing < 0:
        #        cc.sql("insert into tadpole(county, done, total, lastid) values ('%s', 0, %s, 0)" % (
        #            answer.task.info['info']['county'],
        #            answer.task.info['n_answers']))
        #    cc.sql("update tadpole set done = done + 1, lastid = %s where county = '%s'" % (
        #        answer.id,
        #        answer.task.info['info']['county']))
        #    print "."
