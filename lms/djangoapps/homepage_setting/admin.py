from django.contrib import admin
from .models import BannerSetting


# Register your models here.
@admin.register(BannerSetting)
class BannerSettingAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('name', 'url_path',)
    search_fields = ('name',)
    list_editable = ['url_path']
    readonly_fields = ('name',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
