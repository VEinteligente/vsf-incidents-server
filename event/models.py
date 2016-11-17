from __future__ import unicode_literals

from django.db import models
# from Case.models import Case


class Event(models.Model):

    isp = models.CharField(max_length=25)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    target = models.CharField(max_length=25)  # input in metrics
    identification = models.CharField(max_length=50)
    draft = models.BooleanField(default=True)
    # case = models.ForeignKey(Case)
