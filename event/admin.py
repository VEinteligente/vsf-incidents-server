from django.contrib import admin
from models import Event, Site, Url, MutedInput

admin.site.register(Site)
admin.site.register(Url)
admin.site.register(Event)
admin.site.register(MutedInput)
