from __future__ import unicode_literals

from django.db import models
from rest_framework.authtoken.models import Token


class TokenControl(models.Model):
    last_used = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
    token = models.ForeignKey(
                    to=Token, 
                    on_delete=models.CASCADE
                    )

    def __unicode__(self):
        return u'%s' % self.token
