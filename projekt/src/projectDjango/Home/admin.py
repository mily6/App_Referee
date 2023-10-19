from django.contrib import admin

# Register your models here.
from .models import Referee, RefereeAvailability, Message, Secretary, Match, Team
admin.site.register(Referee)
admin.site.register(RefereeAvailability)
admin.site.register(Message)
admin.site.register(Team)
admin.site.register(Match)