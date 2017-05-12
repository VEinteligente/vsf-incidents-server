from django.contrib import admin
from models import Event, Site, Target, MutedInput, SiteCategory

admin.site.register(Site)
admin.site.register(Target)
admin.site.register(Event)
admin.site.register(MutedInput)
admin.site.register(SiteCategory)
