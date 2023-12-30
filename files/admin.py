from django.contrib import admin, messages
from .models import File, Group, FileLock, Checkin, Checkout
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group as G

admin.site.register(File)
admin.site.register(FileLock)
admin.site.register(Checkin)
admin.site.register(Checkout)

class CustomUserAdmin(UserAdmin):
    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        if level == messages.SUCCESS:
            return  # Skip displaying the success message
        super().message_user(request, message, level, extra_tags, fail_silently)
        
    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ValidationError as e:
            self.message_user(request, str(e), level=messages.ERROR)
        else:
            self.message_user(request, "User deleted successfully.", level=messages.SUCCESS)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class FileInline(admin.TabularInline):
    model = File
    extra = 1

class MyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created')
    inlines = [FileInline]


admin.site.unregister(G)
admin.site.register(Group, MyGroupAdmin)