from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CareerGoal(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, related_name='career_goals_requiring')

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    college = models.CharField(max_length=200, blank=True)
    education = models.CharField(max_length=200, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    career_goal = models.ForeignKey(CareerGoal, on_delete=models.SET_NULL, blank=True, null=True)
    current_skills = models.ManyToManyField(Skill, blank=True)
    bio = models.TextField(blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    learning_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class Course(models.Model):
    title = models.CharField(max_length=200)
    course_image = models.ImageField(upload_to='courses/', blank=True, null=True)
    description = models.TextField()
    duration = models.CharField(max_length=100) # e.g. "8 weeks", "40 hours"
    difficulty = models.CharField(
        max_length=50, 
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]
    )
    prerequisites = models.TextField(blank=True)
    learning_outcomes = models.TextField(blank=True)
    career_goal = models.ForeignKey(CareerGoal, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    skills = models.ManyToManyField(Skill, related_name='courses')

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=1)
    theory = models.TextField()
    code_examples = models.TextField(blank=True)
    official_documentation = models.TextField(blank=True)
    practice_problems = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class CodingChallenge(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='coding_challenges', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=50, 
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    )
    xp = models.IntegerField(default=10)
    time_estimate = models.CharField(max_length=50) # e.g. "15 mins"
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    hints = models.TextField(blank=True)
    expected_output = models.TextField()
    solution = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    completed = models.BooleanField(default=False)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.module.title} completed: {self.completed}"

class Quiz(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    xp = models.IntegerField(default=20)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])

    def __str__(self):
        return f"Q: {self.text[:50]}"

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2) # e.g. Percentage
    passed = models.BooleanField(default=False)
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"

class Assignment(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=200)
    description = models.TextField()
    xp = models.IntegerField(default=30)

    def __str__(self):
        return self.title

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_file = models.FileField(upload_to='submissions/')
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], 
        default='Pending'
    )
    grade = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title} - {self.status}"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    date_generated = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} Certificate"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.TextField()
    notification_type = models.CharField(max_length=50, default='info') # info, success, warning, goal, streak etc.
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.user.username} - {self.text[:50]}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    challenge = models.ForeignKey(CodingChallenge, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    date_bookmarked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmark"


class ChallengeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_progress')
    challenge = models.ForeignKey(CodingChallenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    code = models.TextField(blank=True)
    submitted_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - Completed: {self.completed}"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


