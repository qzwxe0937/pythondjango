from django.contrib import admin
from django.urls import reverse
from .models import emLine, emStation, emCheckItem, emFatpDetail, emCheckRecord, emSchedule

from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget


# Register your models here.


class checkItemAdminInline(admin.TabularInline):
    model = emCheckItem


class customStationAdmin(admin.ModelAdmin):
    inlines = (checkItemAdminInline, )

    ordering = ('orderNum',)


class customLineAdmin(admin.ModelAdmin):
    filter_horizontal = ('station', )


class checkItemResource(resources.ModelResource):
    station = fields.Field(
        column_name='station',
        attribute='station',
        widget=ForeignKeyWidget(emStation, 'name'))

    class Meta:
        model = emCheckItem
        import_id_fields = ('checkID',)
        fields = ('station', 'checkID', 'explain', 'size', 'cycleTime')
        export_order = ('station', 'checkID', 'explain', 'size', 'cycleTime')
        skip_unchanged = True


class checkItemAdmin(ImportExportModelAdmin):
    resource_class = checkItemResource

    list_filter = ('station',)


admin.site.register(emCheckItem, checkItemAdmin)

admin.site.register(emLine, customLineAdmin)
admin.site.register(emStation, customStationAdmin)

#admin.site.register(emFatpDetail)
admin.site.register(emCheckRecord)

admin.site.register(emSchedule)


admin.site.site_header = 'A32 FATP EM 管理'
admin.site.site_url = reverse('Index')
