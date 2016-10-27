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

    MED = 'MED'
    DNS = 'DNS'
    TCP = 'TCP'
    HTTP = 'HTTP'

    TYPE_CHOICES = (
        (MED, 'Medicion'),
        (DNS, 'Medicion DNS'),
        (TCP, 'Medicion TCP'),
        (HTTP, 'Medicion HTTP')
    )

    medicion = models.CharField(verbose_name='Id de la Medicion',
                                max_length=40)
    ip = models.GenericIPAddressField()
    # True -> hard, False -> soft, None -> muted
    flag = models.NullBooleanField(default=False)
    type_med = models.CharField(verbose_name='Tipo de Medicion',
                                max_length=50,
                                choices=TYPE_CHOICES,
                                default=MED)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.medicion, self.ip, self.type_med)
