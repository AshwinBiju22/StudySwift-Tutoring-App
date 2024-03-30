from django.urls import include, path
from . import views
from .views import CustomSignupView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
    path("accounts/", include("allauth.urls")),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("self_rev/", views.self_rev, name="self_rev"),
    path("flashcards/create/", views.create_flashcard, name="create_flashcard"),
    path("flashcards/revise/", views.revise_flashcard, name="revise_flashcard"),
    path(
        "flashcards/test/<str:flashcard_ids>/",
        views.test_flashcard,
        name="test_flashcard",
    ),
    path("base_class/", views.base_class, name="base_class"),
    path("manage_classes/", views.manage_classes, name="manage_classes"),
    path("create_class/", views.create_class, name="create_class"),
    path("join_class/", views.join_class, name="join_class"),
    path("leave_class/<str:code>/", views.leave_class, name="leave_class"),
    path("delete_class/<int:class_id>/", views.delete_class, name="delete_class"),
    path(
        "remove_student/<str:code>/<int:student_id>/",
        views.remove_student,
        name="remove_student",
    ),
    path("give_points/<str:student_username>/", views.give_points, name="give_points"),
    path("rewards/", views.rewards_view, name="rewards_view"),
    path(
        "purchase_reward/<int:reward_id>/",
        views.purchase_reward,
        name="purchase_reward",
    ),
    path("manage_homework/", views.manage_homework, name="manage_homework"),
    path("create_homework/", views.create_homework, name="create_homework"),
    path("edit_homework/<int:homework_id>/", views.edit_homework, name="edit_homework"),
    path(
        "delete_homework/<int:homework_id>/",
        views.delete_homework,
        name="delete_homework",
    ),
    path(
        "remove_file/<int:file_id>/<int:homework_id>/",
        views.remove_file,
        name="remove_file",
    ),
    path("view_homework/<int:homework_id>/", views.view_homework, name="view_homework"),
    path(
        "view_submissions/<int:homework_id>/",
        views.view_submissions,
        name="view_submissions",
    ),
    path(
        "class_leaderboard/<int:class_id>/",
        views.class_leaderboard,
        name="class_leaderboard",
    ),
    path("send_message/<int:recipient_id>/", views.send_message, name="send_message"),
    path("inbox/", views.inbox, name="inbox"),
    path("edit-message/<int:message_id>/", views.edit_message, name="edit_message"),
    path(
        "delete-message/<int:message_id>/", views.delete_message, name="delete_message"
    ),
    path("clear-chat/<int:recipient_id>/", views.clear_chat, name="clear_chat"),
    path("calendar_view/", views.calendar_view, name="calendar_view"),
    path("add_event/", views.add_event, name="add_event"),
    path("delete_event/<int:event_id>/", views.delete_event, name="delete_event"),
    path("studybot/", views.bot, name="studybot"),
    path("base_exam/", views.base_exam, name="base_exam"),
    path("create_exam/", views.create_exam, name="create_exam"),
    path(
        "create_questions/<int:exam_id>/",
        views.create_questions,
        name="create_questions",
    ),
    path("take_exam/<int:exam_id>/", views.take_exam, name="take_exam"),
    path(
        "view_exam_submissions/<int:exam_id>/",
        views.view_exam_submissions,
        name="view_exam_submissions",
    ),
    path(
        "exam_results/<str:student_username>/", views.exam_results, name="exam_results"
    ),
    path("update-profile/", views.update_profile, name="update_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
