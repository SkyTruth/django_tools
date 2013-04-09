import appomatic_feedserver.models
import django.contrib.auth.decorators
import django.http
import urllib

def subscribe(request):
    # Don't use @django.contrib.auth.decorators.login_required since we want signup, not signin by default...
    if not request.user.is_authenticated():
        return django.http.HttpResponseRedirect(
            django.core.urlresolvers.reverse('userena.views.signup') +
            "?next=" + urllib.quote_plus(request.get_full_path()))

    if 'l' in request.GET:
        lat1, lng1, lat2, lng2 = [float(x) for x in request.GET['l'].split(',')]
    elif 'BBOX' in request.GET:
        lng1, lat1, lng2, lat2 = [float(x) for x in request.GET['BBOX'].split(',')]

    lngmin = min(lng1, lng2)
    latmin = min(lat1, lat2)
    lngmax = max(lng1, lng2)
    latmax = max(lat1, lat2)

    domain = django.contrib.sites.models.get_current_site(request).domain
    url = django.core.urlresolvers.reverse(appomatic_feedserver.views.feed, kwargs={"format": "rss"})
    query = "?l=%s,%s,%s,%s" % (latmin, lngmin, latmax, lngmax)

    appomatic_feedserver.models.RssEmailSubscription(
            email = request.user.email,
            rss_url = domain + url + query,
            lat1 = latmin,
            lat2 = latmax,
            lng1 = lngmin,
            lng2 = lngmax
       ).save()
    return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_alerts_subscribe_thankyou') + query)
