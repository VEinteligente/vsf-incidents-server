from django.contrib import admin
from models import Event, Site, Url

admin.site.register(Site)
admin.site.register(Url)
admin.site.register(Event)
