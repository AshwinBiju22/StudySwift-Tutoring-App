from django.urls import include, path
from . import views
from .views import CustomSignupView, dashboard #teacher_dashboard


urlpatterns = [
    path('', views.index, name='index'),
    path("portal/", views.portal, name='portal'),

    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),

    path('dashboard/', dashboard, name='dashboard'),
    #path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),

]

