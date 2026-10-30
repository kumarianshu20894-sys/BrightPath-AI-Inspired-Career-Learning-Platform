from django.urls import path
from . import views

urlpatterns = [
    # Auth paths
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("change-password/", views.change_password, name="change_password"),

    # Onboarding
    path("onboarding/", views.onboarding_view, name="onboarding"),

    # Static pages
    path("home/", views.index, name="index_fallback"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # Course paths
    path("course/", views.courses_list, name="courses"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("course/<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),

    # Learning interaction paths
    path("module/<int:module_id>/", views.module_view, name="module_view"),
    path("module/<int:module_id>/complete/", views.mark_module_complete, name="mark_module_complete"),
    path("module/<int:module_id>/run/", views.run_code, name="run_code"),
    path("module/<int:module_id>/submit_challenge/", views.submit_challenge, name="submit_challenge"),
    path("module/<int:module_id>/quiz_submit/", views.submit_quiz, name="submit_quiz"),
    path("module/<int:module_id>/assignment_submit/", views.submit_assignment, name="submit_assignment"),

    # User Profile & Dashboard
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/delete/", views.delete_account, name="delete_account"),
    path("progress/", views.progress, name="progress"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("planner/", views.planner, name="planner"),
    path("quiz/", views.quiz_view, name="quiz"),

    # Projects & Certificates
    path("projects/", views.projects_list, name="projects"),
    path("certificates/", views.certificates_list, name="certificates"),
    path("settings/", views.settings_view, name="settings"),

    # Bookmark & Challenges
    path("bookmark/toggle/", views.toggle_bookmark, name="toggle_bookmark"),
    path("certificate/<int:certificate_id>/pdf/", views.generate_pdf_certificate, name="generate_pdf_certificate"),
    path("challenges/", views.challenges_list, name="challenges"),
    path("playground/", views.coding_playground, name="coding_playground_empty"),
    path("playground/<int:challenge_id>/", views.coding_playground, name="coding_playground"),
    path("playground/autosave/", views.autosave_code, name="autosave_code"),
    path("community/", views.community_view, name="community"),
]


