import appomatic_feedserver.models
import django.contrib.auth.decorators
import django.http
import urllib
import userena.signals
import django.dispatch
import fcdjangoutils.responseutils
import django.shortcuts
import django.contrib.auth.signals
import fcdjangoutils.middleware

def subscribe(request):
    # Don't use @django.contrib.auth.decorators.login_required since we want signup, not signin by default...
    if not request.user.is_authenticated():
        request.session['userena_url_after_activation'] = urllib.quote_plus(request.get_full_path())
        return django.http.HttpResponseRedirect(
            django.core.urlresolvers.reverse('userena.views.signup'))

    if 'l' in request.GET:
        lat1, lng1, lat2, lng2 = [float(x) for x in request.GET['l'].split(',')]
    elif 'BBOX' in request.GET:
        lng1, lat1, lng2, lat2 = [float(x) for x in request.GET['BBOX'].split(',')]

    lngmin = min(lng1, lng2)
    latmin = min(lat1, lat2)
    lngmax = max(lng1, lng2)
    latmax = max(lat1, lat2)

    domain = django.contrib.sites.models.get_current_site(request).domain
    url = django.core.urlresolvers.reverse('appomatic_feedserver.views.feed', kwargs={"format": "rss"})
    query = "?l=%s,%s,%s,%s" % (latmin, lngmin, latmax, lngmax)

    appomatic_feedserver.models.RssEmailSubscription(
            email = request.user.email,
            rss_url = domain + url + query,
            lat1 = latmin,
            lat2 = latmax,
            lng1 = lngmin,
            lng2 = lngmax,
            active = [0, 1][user.is_active()]
       ).save()
    return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse('appomatic_alerts_subscribe_thankyou') + query)


def redirect_after_login(sender, user, **kwargs):
    request = fcdjangoutils.middleware.get_request()
    if 'userena_url_after_activation' in request.session:
        url = request.session.pop('userena_url_after_activation')
        raise fcdjangoutils.responseutils.EarlyResponseException(
            django.shortcuts.redirect(url))
django.dispatch.receiver(userena.signals.signup_complete)(redirect_after_login)
django.dispatch.receiver(django.contrib.auth.signals.user_logged_in)(redirect_after_login)


@django.dispatch.receiver(userena.signals.activation_complete)
def my_callback(sender, user, **kwargs):
    for subscr in appomatic_feedserver.models.RssEmailSubscription.objects.filter(email = user.email):
        subscr.active = 1
        subscr.save()
