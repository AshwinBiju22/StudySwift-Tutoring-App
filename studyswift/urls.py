from django.urls import include, path
from . import views
from .views import CustomSignupView, dashboard


urlpatterns = [
    path('', views.index, name='index'),
    path("portal/", views.portal, name='portal'),

    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),

    path('dashboard/', dashboard, name='dashboard'),

    path('self_rev/', views.self_rev, name='self_rev'),
    path('flashcards/create/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/revise/', views.revise_flashcard, name='revise_flashcard'),
    path('flashcards/test/<str:flashcard_ids>/', views.test_flashcard, name='test_flashcard'),

]

