from __future__ import unicode_literals

from django.db import models


class DNS(models.Model):

    isp = models.CharField(verbose_name='Operadora', max_length=50)
    verbose = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s - %s" % (self.verbose, self.ip)


class Flag(models.Model):

    medicion = models.CharField(verbose_name='Id de la Medicion',
                                max_length=40)
    # True -> hard, False -> soft, None -> muted
    flag = models.NullBooleanField(default=False)

    def __unicode__(self):
        return u"%s" % (self.medicion)
