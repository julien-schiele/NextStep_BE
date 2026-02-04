from django.contrib import admin
from .models import UserProgram, UserProgramSession, UserProgramFeedback

admin.site.register(UserProgram)
admin.site.register(UserProgramSession)
admin.site.register(UserProgramFeedback)
