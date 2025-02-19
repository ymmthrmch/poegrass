from . import views
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import path

app_name = "utakais"

urlpatterns = [
    path('events/<int:pk>/admin/', views.EventAdminView.as_view(), name="event_admin"),
    path('events/<int:pk>/download/<str:file_type>/',views.download_eisou_file,name="download_eisou_file"),
    path('events/<int:pk>/execute_method/<str:method_name>/', views.execute_method, {'app_name': 'utakais', 'model_name': 'Event'}, name='execute_method'),
    path('events/<int:pk>/',views.change_event_view,name="event_detail"),
    path('events/create/',views.EventCreateView.as_view(),name="event_create"),
#    path('tankas/<int:pk>/edit',views.TankaEditView.as_view(),name="tanka_edit"),
    path('tankas/<int:pk>/',views.TankaDetailView.as_view(),name="tanka_detail"),
#    path('tankas/create/',views.TankaCreateView.as_view(),name="tanka_create"),
#    path('tankas/',views.TankaIndexView.as_view(),name="tanka_index"),
    path('',views.EventIndexView.as_view(),name="events_index"),
]