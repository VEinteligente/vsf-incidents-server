from django.contrib import admin
from models import Event, Site, Target, MutedInput

admin.site.register(Site)
admin.site.register(Target)
admin.site.register(Event)
admin.site.register(MutedInput)
