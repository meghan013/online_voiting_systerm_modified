# poll/admin.py

from django.contrib import admin
from .models import Candidate, Position, ControlVote, VoterID

admin.site.register(Candidate)
admin.site.register(Position)
admin.site.register(ControlVote)
admin.site.register(VoterID)
