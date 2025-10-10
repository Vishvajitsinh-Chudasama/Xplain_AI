from django.contrib import admin
from .models import UserInfo  # only import UserInfo

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')  # columns visible in admin
    search_fields = ('name', 'email', 'phone')  # search by these fields
    list_filter = ('created_at',)  # filter by creation date
