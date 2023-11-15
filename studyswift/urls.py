from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("portal/", views.portal, name='portal'),
    path('accounts/', include('allauth.urls')),

    path("dashboard/", views.dashboard, name='dashboard'),
    
]