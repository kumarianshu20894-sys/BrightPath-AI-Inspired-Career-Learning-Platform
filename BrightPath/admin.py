from django.contrib import admin
from .models import (
    Skill, CareerGoal, Profile, Course, Module, 
    CodingChallenge, Enrollment, Progress, Quiz, 
    Question, Result, Assignment, Submission, 
    Certificate, Notification, Bookmark
)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'career_goal', 'xp', 'level', 'learning_streak')
    list_filter = ('career_goal', 'level')
    search_fields = ('user__username', 'user__email', 'college')

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'duration', 'career_goal')
    list_filter = ('difficulty', 'career_goal')
    search_fields = ('title', 'description')
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'theory')
    ordering = ('course', 'order')

@admin.register(CodingChallenge)
class CodingChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'difficulty', 'xp')
    list_filter = ('difficulty', 'module__course')
    search_fields = ('title', 'description')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed', 'enrolled_date')
    list_filter = ('completed', 'course')
    search_fields = ('user__username', 'course__title')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed', 'completed_date')
    list_filter = ('completed', 'module__course')
    search_fields = ('user__username', 'module__title')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'xp')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_option')
    list_filter = ('quiz',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'date_taken')
    list_filter = ('passed', 'quiz')
    search_fields = ('user__username', 'quiz__title')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'xp')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'status', 'grade', 'date_submitted')
    list_filter = ('status', 'assignment')
    search_fields = ('user__username', 'assignment__title')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'verification_code', 'date_generated')
    search_fields = ('user__username', 'course__title', 'verification_code')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'notification_type', 'is_read', 'date_created')
    list_filter = ('is_read', 'notification_type')
    search_fields = ('user__username', 'text')

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'module', 'challenge', 'date_bookmarked')
