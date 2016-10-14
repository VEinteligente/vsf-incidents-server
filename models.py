# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Metrics(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    input = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    report_filename = models.TextField(blank=True, null=True)
    options = models.TextField(blank=True, null=True)  # This field type is a guess.
    probe_cc = models.TextField(blank=True, null=True)
    probe_asn = models.TextField(blank=True, null=True)
    probe_ip = models.TextField(blank=True, null=True)
    data_format_version = models.TextField(blank=True, null=True)
    test_name = models.TextField(blank=True, null=True)
    test_start_time = models.DateTimeField(blank=True, null=True)
    measurement_start_time = models.DateTimeField(blank=True, null=True)
    test_runtime = models.FloatField(blank=True, null=True)
    test_helpers = models.TextField(blank=True, null=True)  # This field type is a guess.
    test_keys = models.TextField(blank=True, null=True)  # This field type is a guess.
    software_name = models.TextField(blank=True, null=True)
    software_version = models.TextField(blank=True, null=True)
    test_version = models.TextField(blank=True, null=True)
    bucket_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metrics'


class TableUpdates(models.Model):
    update_id = models.TextField(primary_key=True)
    target_table = models.TextField(blank=True, null=True)
    inserted = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'table_updates'
