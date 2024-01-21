from django.urls import include, path
from . import views
from .views import CustomSignupView


urlpatterns = [
    path("", views.homepage, name='homepage'),

    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('self_rev/', views.self_rev, name='self_rev'),
    path('flashcards/create/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/revise/', views.revise_flashcard, name='revise_flashcard'),
    path('flashcards/test/<str:flashcard_ids>/', views.test_flashcard, name='test_flashcard'),

    path('base_class/', views.base_class, name='base_class'),
    path('manage_classes/', views.manage_classes, name='manage_classes'),
    path('create_class/', views.create_class, name='create_class'),
    path('join_class/', views.join_class, name='join_class'),
    path('leave_class/<str:code>/', views.leave_class, name='leave_class'),

    path('give_points/<str:student_username>/', views.give_points, name='give_points'),
    path("rewards/", views.rewards_view, name='rewards_view'),
    path('purchase_reward/<int:reward_id>/', views.purchase_reward, name='purchase_reward'),
]

