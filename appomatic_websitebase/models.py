import userena.models
import django.db.models
import django.contrib.auth.models
from django.utils.translation import ugettext as _

class Profile(userena.models.UserenaBaseProfile):
    user = django.db.models.OneToOneField(django.contrib.auth.models.User,
                                          unique=True,
                                          verbose_name=_('user'),
                                          related_name='profile')

    def get_absolute_url(self):
        return django.core.urlresolvers.reverse("userena.views.profile", kwargs={'username': self.user.username})
