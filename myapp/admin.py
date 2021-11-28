from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EnrollRequest)
admin.site.register(Courses)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Comment)
admin.site.register(DirectMessage)
admin.site.register(DiscussionForum)