from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("portal/", views.portal, name='portal'),
    path('accounts/', include('allauth.urls')),

    path("menu/", views.menu, name='menu'),
    
]