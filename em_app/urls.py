from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.Index, name='Index'),
    url(r'^index/$', views.Index, name='Index'),

    url(r'^detail/(?P<line>[a-z]{5})/$', views.Detail, name='Detail'),

    url(r'^schedule/(?P<line>[a-z]{5})/$', views.Schedule, name='Schedule'),

    url(r'^form/(?P<line>[a-z]{5})/all/$', views.FormAll, name='FormAll'),
    url(r'^form/(?P<line>[a-z]{5})/(?P<station>[a-z]{2})/$',
        views.Form, name='Form'),

    url(r'^record/(?P<line>[a-z]{5})/all/$',
        views.RecordAll, name='RecordAll'),
    url(r'^record/(?P<line>[a-z]{5})/(?P<station>[a-z]{2})/$',
        views.Record, name='Record'),

    url(r'^record/download/(?P<record_id>\d+)/$',
        views.RecordFileDownload, name='recordFileDownload'),

    url(r'^schedule/upload/$', views.scheduleUpload, name='scheduleUpload'),

    #url(r'^UploadTestData/$', views.UploadTestData, name='UploadTestData'),
]
