from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('record/add/', views.add_or_edit_record, name='add_record'),
    path('record/<int:record_id>/edit/', views.add_or_edit_record, name='edit_record'),
    path('history/', views.history, name='history'),
    path('stats/', views.stats, name='stats'),
]
