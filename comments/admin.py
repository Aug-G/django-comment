from django.contrib import admin
from .models import  Thread, Comment


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

