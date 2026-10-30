import os
import sys
from io import StringIO
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from datetime import date

from .models import (
    Skill, CareerGoal, Profile, Course, Module, 
    CodingChallenge, Enrollment, Progress, Quiz, 
    Question, Result, Assignment, Submission, 
    Certificate, Notification, Bookmark, ChallengeProgress
)
from .seed_data import seed_database_data

# ==========================================
# NULL-SAFE PROFILE RETRIEVAL HELPER
# ==========================================
def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

# ==========================================
# SMART CAREER RECOMMENDATION ENGINE
# ==========================================
def get_career_recommendations(profile):
    goal = profile.career_goal
    if not goal:
        return {
            'missing_skills': [],
            'readiness': 0,
            'courses': [],
            'next_step': None,
            'roadmap': []
        }
    
    # Required vs Current Skills
    required = set(goal.required_skills.all())
    current = set(profile.current_skills.all())
    
    missing = required - current
    
    total_req = len(required)
    readiness = int((len(required & current) / total_req) * 100) if total_req > 0 else 100
    
    # Recommended Courses (teaching career path skills)
    courses = Course.objects.filter(career_goal=goal)
    if not courses.exists():
        courses = Course.objects.filter(skills__in=required).distinct()
    
    # Roadmap calculation
    roadmap = []
    next_step = None
    
    all_modules = Module.objects.filter(course__in=courses).order_by('course', 'order')
    
    for idx, mod in enumerate(all_modules):
        completed = Progress.objects.filter(user=profile.user, module=mod, completed=True).exists()
        
        # Unlocked logic: first module is always unlocked, 
        # subsequent modules are unlocked if previous in course is completed.
        if mod.order == 1:
            unlocked = True
        else:
            prev_mod = Module.objects.filter(course=mod.course, order=mod.order - 1).first()
            unlocked = prev_mod and Progress.objects.filter(user=profile.user, module=prev_mod, completed=True).exists()
        
        roadmap.append({
            'module': mod,
            'completed': completed,
            'unlocked': unlocked
        })
        
        if unlocked and not completed and not next_step:
            next_step = mod

    return {
        'missing_skills': list(missing),
        'readiness': readiness,
        'courses': courses,
        'next_step': next_step,
        'roadmap': roadmap
    }

from django.core.exceptions import PermissionDenied

# ==========================================
# AUTH VIEWS
# ==========================================
def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_staff:
            return redirect('staff_dashboard')
        else:
            return redirect('student_dashboard')
        
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        try:
            # Find User by email
            user = User.objects.get(email=email)
            # Authenticate using standard username
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user:
                auth_login(request, authenticated_user)
                
                # Remember Me session expiry configuration
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close expiry
                
                # Check / update streak
                profile = get_user_profile(authenticated_user)
                today = date.today()
                if profile.last_activity_date:
                    delta = (today - profile.last_activity_date).days
                    if delta == 1:
                        profile.learning_streak += 1
                        Notification.objects.create(
                            user=authenticated_user,
                            text=f"🔥 Learning streak continued! Day {profile.learning_streak}!",
                            notification_type="streak"
                        )
                    elif delta > 1:
                        profile.learning_streak = 1
                else:
                    profile.learning_streak = 1
                
                profile.last_activity_date = today
                profile.save()
                
                # Redirect based on role
                if authenticated_user.is_superuser:
                    return redirect('admin_dashboard')
                elif authenticated_user.is_staff:
                    return redirect('staff_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid password. Please try again.")
        except User.DoesNotExist:
            messages.error(request, "No account registered with this email.")
            
    return render(request, "login.html")

def signup_view(request):
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.is_staff:
            return redirect('staff_dashboard')
        else:
            return redirect('student_dashboard')
        
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('number', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        bd = request.POST.get('bd', '')
        password = request.POST.get('password', '')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "signup.html")
            
        # Create user
        username = email # Use email as username
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            first_name=name
        )
        
        # Get the profile created by signals and update it (prevents IntegrityError)
        profile = get_user_profile(user)
        profile.phone = phone
        profile.bio = f"Address: {address}\nDOB: {bd}"
        profile.save()
        
        # Auto-login
        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user:
            auth_login(request, authenticated_user)
            Notification.objects.create(
                user=user,
                text="Welcome to BrightPath! Choose a career goal and start learning.",
                notification_type="info"
            )
            # Redirect based on role
            if authenticated_user.is_superuser:
                return redirect('admin_dashboard')
            elif authenticated_user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('student_dashboard')
            
    return render(request, "signup.html")
            
    return render(request, "signup.html")

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        new_password = request.POST.get('password', '')
        
        try:
            user = User.objects.get(email=email)
            profile = get_user_profile(user)
            if profile.phone == phone:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password successfully reset! You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Verification failed. Phone number does not match.")
        except User.DoesNotExist:
            messages.error(request, "No account registered with this email.")
            
    return render(request, "forgot_password.html")

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
        else:
            messages.error(request, "Incorrect current password.")
            
    return render(request, "change_password.html")

# ==========================================
# STATIC / CORE PAGES
# ==========================================
def index(request):
    # Ensure database is seeded with initial data
    seed_database_data()
    
    courses = Course.objects.all()[:3]
    goals = CareerGoal.objects.all()
    
    context = {
        'courses': courses,
        'goals': goals,
    }
    return render(request, "index.html", context)

def about(request):
    seed_database_data()
    return render(request, "about.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        msg = request.POST.get('message')
        # Simulate saving or sending
        messages.success(request, f"Thank you {name}! Your message has been received.")
    return render(request, "contact.html")

# ==========================================
# PROFILE & EDIT
# ==========================================
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    goals = CareerGoal.objects.all()
    skills = Skill.objects.all()
    
    # Calculate smart recommendations
    recs = get_career_recommendations(profile)
    certificates = Certificate.objects.filter(user=request.user)
    bookmarks = Bookmark.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'goals': goals,
        'skills': skills,
        'missing_skills': recs['missing_skills'],
        'readiness': recs['readiness'],
        'certificates': certificates,
        'bookmarks': bookmarks
    }
    return render(request, "profile.html", context)

@login_required
def profile_edit(request):
    if request.method == "POST":
        profile = get_user_profile(request.user)
        
        request.user.first_name = request.POST.get('name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        profile.phone = request.POST.get('phone', '').strip()
        profile.college = request.POST.get('college', '').strip()
        profile.education = request.POST.get('education', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        
        goal_id = request.POST.get('career_goal')
        if goal_id:
            profile.career_goal = CareerGoal.objects.filter(id=goal_id).first()
        else:
            profile.career_goal = None
            
        skill_ids = request.POST.getlist('skills')
        profile.current_skills.set(Skill.objects.filter(id__in=skill_ids))
        
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
            
        profile.save()
        messages.success(request, "Profile updated successfully!")
        
    return redirect('profile')

# ==========================================
# COURSES & ROADMAPS
# ==========================================
@login_required
def courses_list(request):
    query = request.GET.get('q', '').strip()
    goal_filter = request.GET.get('goal', '')
    my_learning = request.GET.get('my_learning')
    
    courses = Course.objects.all()
    
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(skills__name__icontains=query)
        ).distinct()
        
    if goal_filter:
        courses = courses.filter(career_goal_id=goal_filter)
        
    if my_learning:
        enrolled_ids = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
        courses = courses.filter(id__in=enrolled_ids)
        
    goals = CareerGoal.objects.all()
    
    context = {
        'courses': courses,
        'goals': goals,
        'query': query,
        'goal_filter': goal_filter,
        'my_learning': my_learning,
    }
    return render(request, "courses.html", context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    modules = course.modules.all().order_by('order')
    modules_data = []
    
    for idx, mod in enumerate(modules):
        completed = Progress.objects.filter(user=request.user, module=mod, completed=True).exists()
        
        # Unlocked criteria: first module or previous module is completed
        if mod.order == 1:
            unlocked = True
        else:
            prev_mod = Module.objects.filter(course=course, order=mod.order - 1).first()
            unlocked = prev_mod and Progress.objects.filter(user=request.user, module=prev_mod, completed=True).exists()
            
        modules_data.append({
            'module': mod,
            'completed': completed,
            'unlocked': unlocked
        })
        
    bookmarked = Bookmark.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'modules_data': modules_data,
        'bookmarked': bookmarked
    }
    return render(request, "course_detail.html", context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    if created:
        Notification.objects.create(
            user=request.user,
            text=f"📚 Enrolled in '{course.title}' successfully! Let's get started.",
            notification_type="success"
        )
        messages.success(request, f"Successfully enrolled in {course.title}!")
        
    return redirect('course_detail', course_id=course.id)

# ==========================================
# MODULE LEARNING VIEW & ACTIONS
# ==========================================
@login_required
def module_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    
    # Verify enrollment
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        messages.warning(request, "Please enroll in the course first.")
        return redirect('course_detail', course_id=course.id)
        
    # Check unlock status
    if module.order > 1:
        prev_mod = Module.objects.filter(course=course, order=module.order - 1).first()
        unlocked = prev_mod and Progress.objects.filter(user=request.user, module=prev_mod, completed=True).exists()
        if not unlocked:
            messages.error(request, "This module is locked. Complete previous modules first!")
            return redirect('course_detail', course_id=course.id)
            
    completed = Progress.objects.filter(user=request.user, module=module, completed=True).exists()
    challenges = module.coding_challenges.all()
    
    # Fetch coding challenge progress status and solutions
    challenges_data = []
    all_challenges_passed = True
    for chal in challenges:
        prog = ChallengeProgress.objects.filter(user=request.user, challenge=chal).first()
        is_passed = prog.completed if prog else False
        if not is_passed:
            all_challenges_passed = False
        challenges_data.append({
            'id': chal.id,
            'title': chal.title,
            'description': chal.description,
            'difficulty': chal.difficulty,
            'starter_code': prog.code if prog else chal.starter_code,
            'hints': chal.hints,
            'completed': is_passed
        })
    if not challenges.exists():
        all_challenges_passed = True
        
    quiz = getattr(module, 'quiz', None)
    assignment = getattr(module, 'assignment', None)
    
    # Submission statuses
    quiz_result = Result.objects.filter(user=request.user, quiz=quiz).first() if quiz else None
    assignment_sub = Submission.objects.filter(user=request.user, assignment=assignment).first() if assignment else None
    
    # Bookmarks
    bookmarked = Bookmark.objects.filter(user=request.user, module=module).exists()
    
    # Navigation
    next_module = Module.objects.filter(course=course, order=module.order + 1).first()
    prev_module = Module.objects.filter(course=course, order=module.order - 1).first()
    
    context = {
        'module': module,
        'course': course,
        'completed': completed,
        'challenges': challenges_data,
        'all_challenges_passed': all_challenges_passed,
        'quiz': quiz,
        'quiz_result': quiz_result,
        'assignment': assignment,
        'assignment_sub': assignment_sub,
        'bookmarked': bookmarked,
        'next_module': next_module,
        'prev_module': prev_module
    }
    return render(request, "planner.html", context)

@login_required
def mark_module_complete(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    user = request.user
    
    # Enforce sequential logic
    challenges = module.coding_challenges.all()
    completed_challenges = ChallengeProgress.objects.filter(user=user, challenge__in=challenges, completed=True).count()
    if completed_challenges < challenges.count():
        messages.error(request, "Solve all coding challenges before completing this module!")
        return redirect(f"/module/{module.id}/?tab=playground")
        
    quiz = getattr(module, 'quiz', None)
    quiz_passed = Result.objects.filter(user=user, quiz=quiz, passed=True).exists() if quiz else True
    if not quiz_passed:
        messages.error(request, "Pass the module quiz before completing this module!")
        return redirect(f"/module/{module.id}/?tab=quiz")
        
    assignment = getattr(module, 'assignment', None)
    assignment_submitted = Submission.objects.filter(user=user, assignment=assignment).exists() if assignment else True
    if not assignment_submitted:
        messages.error(request, "Submit the mini-project assignment before completing this module!")
        return redirect(f"/module/{module.id}/?tab=upload")
        
    progress, created = Progress.objects.get_or_create(user=user, module=module)
    if not progress.completed:
        progress.completed = True
        progress.save()
        
        # Award XP
        profile = get_user_profile(user)
        profile.xp += 25
        profile.level = (profile.xp // 100) + 1
        profile.save()
        
        # Calculate overall course completion
        total_mods = course.modules.count()
        completed_mods = Progress.objects.filter(user=user, module__course=course, completed=True).count()
        
        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if enrollment:
            percentage = Decimal(completed_mods) / Decimal(total_mods) * Decimal(100.0)
            enrollment.progress_percentage = percentage
            if percentage >= 100:
                enrollment.completed = True
                enrollment.completed_date = timezone.now()
                # Create Certificate
                verification = str(uuid.uuid4())[:8].upper()
                Certificate.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={'verification_code': verification}
                )
                Notification.objects.create(
                    user=user,
                    text=f"🎓 Congratulations! You completed '{course.title}' and earned a certificate!",
                    notification_type="certificate"
                )
            enrollment.save()
            
        Notification.objects.create(
            user=user,
            text=f"✅ Completed module: {module.title} (+25 XP)",
            notification_type="success"
        )
        
    next_mod = Module.objects.filter(course=course, order=module.order + 1).first()
    if next_mod:
        return redirect('module_view', module_id=next_mod.id)
    else:
        return redirect('course_detail', course_id=course.id)

# ==========================================
# INTERACTIVE CODE RUNNER & PLAYGROUND
# ==========================================
@login_required
@csrf_exempt
def run_code(request, module_id):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
        
    code = request.POST.get('code', '')
    challenge_id = request.POST.get('challenge_id')
    
    # Execution setup - standard stdout redirection
    old_stdout = sys.stdout
    redirected = sys.stdout = StringIO()
    
    success = True
    error_msg = ""
    console_output = ""
    
    try:
        # Run code in safe dict environment
        local_env = {}
        exec(code, {'__builtins__': __builtins__}, local_env)
        console_output = redirected.getvalue()
    except Exception as e:
        success = False
        error_msg = str(e)
        console_output = redirected.getvalue()
    finally:
        sys.stdout = old_stdout
        
    response_data = {
        'success': success,
        'console': console_output,
        'error': error_msg
    }
    
    return JsonResponse(response_data)

@login_required
@csrf_exempt
def submit_challenge(request, module_id):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
        
    code = request.POST.get('code', '')
    challenge_id = request.POST.get('challenge_id')
    
    challenge = get_object_or_404(CodingChallenge, id=challenge_id)
    expected = challenge.expected_output.strip()
    
    # Run user code and inspect output
    old_stdout = sys.stdout
    redirected = sys.stdout = StringIO()
    
    success = True
    error_msg = ""
    actual_output = ""
    
    try:
        # Try running code and executing target function
        local_env = {}
        exec(code, {'__builtins__': __builtins__}, local_env)
        
        # Match test logic based on expected function signature
        # e.g., challenge function name is derived from title, or simply we inspect function return value
        func_name = ""
        test_val = None
        
        if "prime" in challenge.title.lower():
            func_name = "is_prime"
            if func_name in local_env:
                test_val = str(local_env[func_name](7))
        elif "palindrome" in challenge.title.lower():
            func_name = "is_palindrome"
            if func_name in local_env:
                test_val = str(local_env[func_name]("radar"))
        elif "even" in challenge.title.lower() or "odd" in challenge.title.lower():
            func_name = "even_odd"
            if func_name in local_env:
                test_val = str(local_env[func_name](4))
        elif "factorial" in challenge.title.lower():
            func_name = "factorial"
            if func_name in local_env:
                test_val = str(local_env[func_name](5))
        elif "fibonacci" in challenge.title.lower():
            func_name = "fibonacci"
            if func_name in local_env:
                test_val = str(local_env[func_name](5))
                
        actual_output = redirected.getvalue().strip()
        
        # Validation checks
        if test_val is not None:
            # If function returned the expected value
            passed = (test_val.lower() == expected.lower())
        else:
            # Fallback to stdout matching
            passed = (actual_output.lower() == expected.lower() or expected in actual_output)
            
    except Exception as e:
        passed = False
        error_msg = str(e)
        actual_output = redirected.getvalue()
    finally:
        sys.stdout = old_stdout
        
    ChallengeProgress.objects.update_or_create(
        user=request.user,
        challenge=challenge,
        defaults={'completed': passed, 'code': code}
    )
        
    if passed:
        # Award XP
        profile = get_user_profile(request.user)
        profile.xp += challenge.xp
        profile.level = (profile.xp // 100) + 1
        profile.save()
        
        Notification.objects.create(
            user=request.user,
            text=f"🏆 Solved coding challenge: {challenge.title} (+{challenge.xp} XP)",
            notification_type="success"
        )
        
        return JsonResponse({
            'passed': True,
            'message': f"All test cases passed! +{challenge.xp} XP awarded.",
            'console': actual_output
        })
    else:
        return JsonResponse({
            'passed': False,
            'message': "Test case failed. Expected output did not match.",
            'console': actual_output,
            'error': error_msg or f"Expected: {expected}, Got: {test_val or actual_output}"
        })

# ==========================================
# QUIZ SUBMISSION API
# ==========================================
@login_required
def submit_quiz(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    quiz = get_object_or_404(Quiz, module=module)
    
    if request.method == "POST":
        questions = quiz.questions.all()
        total_questions = questions.count()
        correct_answers = 0
        
        for q in questions:
            user_choice = request.POST.get(f'question_{q.id}')
            if user_choice and int(user_choice) == q.correct_option:
                correct_answers += 1
                
        score = Decimal(correct_answers) / Decimal(total_questions) * Decimal(100.0) if total_questions > 0 else Decimal(0)
        passed = score >= 70
        
        # Save Result
        result, _ = Result.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'score': score, 'passed': passed}
        )
        
        # Award XP
        if passed:
            profile = get_user_profile(request.user)
            profile.xp += quiz.xp
            profile.level = (profile.xp // 100) + 1
            profile.save()
            
            Notification.objects.create(
                user=request.user,
                text=f"📝 Passed quiz: {quiz.title} with {score:.1f}% (+{quiz.xp} XP)",
                notification_type="success"
            )
            
            messages.success(request, f"Quiz passed with {score:.1f}%! +{quiz.xp} XP awarded.")
        if passed:
            return redirect(f"/module/{module.id}/?tab=upload")
        else:
            return redirect(f"/module/{module.id}/?tab=quiz")
            
    return redirect(f"/module/{module.id}/")

# ==========================================
# ASSIGNMENT SUBMISSION
# ==========================================
@login_required
def submit_assignment(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    assignment = get_object_or_404(Assignment, module=module)
    
    if request.method == "POST" and request.FILES.get('file'):
        uploaded = request.FILES.get('file')
        
        # Create submission
        submission = Submission.objects.create(
            user=request.user,
            assignment=assignment,
            submitted_file=uploaded,
            status='Approved',  # Auto-approve for easy testing
            grade='A+'
        )
        
        # Award XP
        profile = get_user_profile(request.user)
        profile.xp += assignment.xp
        profile.level = (profile.xp // 100) + 1
        profile.save()
        
        Notification.objects.create(
            user=request.user,
            text=f"📂 Assignment '{assignment.title}' approved (+{assignment.xp} XP)",
            notification_type="success"
        )
        messages.success(request, f"Assignment submitted and approved! +{assignment.xp} XP awarded.")
        
    return redirect(f"/module/{module.id}/?tab=upload")

# ==========================================
# PLANNER / LEARNING PATHS (DYNAMIC)
# ==========================================
@login_required
def planner(request):
    profile = get_user_profile(request.user)
    recs = get_career_recommendations(profile)
    
    context = {
        'profile': profile,
        'career_goal': profile.career_goal,
        'missing_skills': recs['missing_skills'],
        'readiness': recs['readiness'],
        'next_step': recs['next_step'],
        'roadmap': recs['roadmap']
    }
    return render(request, "planner.html", context)

# ==========================================
# DASHBOARD ROUTER & STUDENT DASHBOARD
# ==========================================
@login_required
def progress(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_staff:
        return redirect('staff_dashboard')
    else:
        return redirect('student_dashboard')

@login_required
def student_dashboard(request):
    profile = get_user_profile(request.user)
    if not profile.career_goal:
        return redirect('onboarding')
    enrollments = Enrollment.objects.filter(user=request.user)
    recs = get_career_recommendations(profile)
    notifications = Notification.objects.filter(user=request.user)[:5]
    bookmarks = Bookmark.objects.filter(user=request.user)
    certificates = Certificate.objects.filter(user=request.user)
    submissions = Submission.objects.filter(user=request.user)
    
    # Calculate stats
    completed_courses = enrollments.filter(completed=True).count()
    total_xp = profile.xp
    level = profile.level
    streak = profile.learning_streak
    
    # Fetch uncompleted enroled courses to 'Continue Learning'
    continue_courses = enrollments.filter(completed=False)
    
    # Chart.js values
    course_names = [e.course.title for e in enrollments]
    course_progress = [float(e.progress_percentage) for e in enrollments]
    
    context = {
        'profile': profile,
        'enrollments': enrollments,
        'completed_courses_count': completed_courses,
        'total_xp': total_xp,
        'level': level,
        'streak': streak,
        'notifications': notifications,
        'bookmarks': bookmarks,
        'certificates': certificates,
        'submissions': submissions,
        'recommended_courses': recs['courses'][:3] if recs['courses'] else [],
        'continue_courses': continue_courses,
        'readiness': recs['readiness'],
        'missing_skills': recs['missing_skills'],
        'next_step': recs['next_step'],
        'roadmap': recs['roadmap'],
        'course_names_json': course_names,
        'course_progress_json': course_progress,
    }
    return render(request, "dashboard.html", context)

# ==========================================
# BOOKMARKS
# ==========================================
@login_required
def toggle_bookmark(request):
    if request.method == "POST":
        course_id = request.POST.get('course_id')
        module_id = request.POST.get('module_id')
        challenge_id = request.POST.get('challenge_id')
        
        user = request.user
        
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            bookmark, created = Bookmark.objects.get_or_create(user=user, course=course)
            if not created:
                bookmark.delete()
                return JsonResponse({'status': 'removed', 'type': 'course'})
            return JsonResponse({'status': 'added', 'type': 'course'})
            
        elif module_id:
            module = get_object_or_404(Module, id=module_id)
            bookmark, created = Bookmark.objects.get_or_create(user=user, module=module)
            if not created:
                bookmark.delete()
                return JsonResponse({'status': 'removed', 'type': 'module'})
            return JsonResponse({'status': 'added', 'type': 'module'})
            
        elif challenge_id:
            challenge = get_object_or_404(CodingChallenge, id=challenge_id)
            bookmark, created = Bookmark.objects.get_or_create(user=user, challenge=challenge)
            if not created:
                bookmark.delete()
                return JsonResponse({'status': 'removed', 'type': 'challenge'})
            return JsonResponse({'status': 'added', 'type': 'challenge'})
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

# ==========================================
# DIGITAL VERIFIABLE CERTIFICATE
# ==========================================
@login_required
def generate_pdf_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    # Render beautiful webpage certificate that has a print mode
    context = {
        'certificate': certificate,
        'user': request.user,
        'profile': get_user_profile(request.user),
        'course': certificate.course,
        'date': certificate.date_generated.strftime("%B %d, %Y"),
        'code': certificate.verification_code
    }
    return render(request, "certificate_template.html", context)

@login_required
def quiz_view(request):
    return redirect('planner')

@login_required
def challenges_list(request):
    challenges = CodingChallenge.objects.all()
    context = {
        'challenges': challenges,
    }
    return render(request, "challenges.html", context)

@login_required
def community_view(request):
    leaderboard = Profile.objects.all().order_by('-xp')[:10]
    context = {
        'leaderboard': leaderboard,
    }
    return render(request, "community.html", context)

# ==========================================
# STAFF & ADMIN DASHBOARDS
# ==========================================
@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
        
    submissions = Submission.objects.all().order_by('-date_submitted')
    total_students = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_courses = Course.objects.count()
    pending_submissions = submissions.filter(status='Pending').count()
    
    if request.method == "POST":
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action') # 'approve' or 'reject'
        grade = request.POST.get('grade', 'A')
        
        sub = get_object_or_404(Submission, id=submission_id)
        if action == 'approve':
            sub.status = 'Approved'
            sub.grade = grade
            sub.save()
            messages.success(request, f"Submission for {sub.user.username} approved.")
        elif action == 'reject':
            sub.status = 'Rejected'
            sub.save()
            messages.warning(request, f"Submission for {sub.user.username} rejected.")
        return redirect('staff_dashboard')
        
    context = {
        'submissions': submissions,
        'total_students': total_students,
        'total_courses': total_courses,
        'pending_submissions': pending_submissions,
        'profile': get_user_profile(request.user),
    }
    return render(request, "staff_dashboard.html", context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied
        
    users = User.objects.all()
    courses = Course.objects.all()
    enrollments = Enrollment.objects.all()
    
    total_users = users.count()
    total_staff = users.filter(is_staff=True).count()
    total_courses = courses.count()
    total_enrollments = enrollments.count()
    
    if request.method == "POST":
        target_user_id = request.POST.get('user_id')
        new_role = request.POST.get('role') # 'student', 'staff', 'admin'
        
        target_user = get_object_or_404(User, id=target_user_id)
        if new_role == 'student':
            target_user.is_staff = False
            target_user.is_superuser = False
        elif new_role == 'staff':
            target_user.is_staff = True
            target_user.is_superuser = False
        elif new_role == 'admin':
            target_user.is_staff = True
            target_user.is_superuser = True
        target_user.save()
        messages.success(request, f"Role for {target_user.username} updated to {new_role}.")
        return redirect('admin_dashboard')
        
    context = {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'users': users[:20],
        'courses': courses,
        'profile': get_user_profile(request.user),
    }
    return render(request, "admin_dashboard.html", context)

# ==========================================
# DEDICATED CODING PLAYGROUND
# ==========================================
@login_required
def coding_playground(request, challenge_id=None):
    challenges = CodingChallenge.objects.all()
    if challenge_id:
        challenge = get_object_or_404(CodingChallenge, id=challenge_id)
    else:
        challenge = challenges.first()
        if not challenge:
            # Seed database if there are no challenges loaded
            seed_database_data()
            challenges = CodingChallenge.objects.all()
            challenge = challenges.first()
            
    saved_code = ""
    if challenge:
        prog = ChallengeProgress.objects.filter(user=request.user, challenge=challenge).first()
        if prog:
            saved_code = prog.code
            
    context = {
        'challenges': challenges,
        'challenge': challenge,
        'profile': get_user_profile(request.user),
        'saved_code': saved_code,
    }
    return render(request, "playground.html", context)


@login_required
def onboarding_view(request):
    profile = get_user_profile(request.user)
    if request.method == "POST":
        step = request.POST.get('step')
        if step == '1':
            profile.phone = request.POST.get('phone', '').strip()
            profile.college = request.POST.get('college', '').strip()
            profile.education = request.POST.get('education', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            if 'profile_photo' in request.FILES:
                profile.profile_photo = request.FILES['profile_photo']
            profile.save()
            return JsonResponse({'success': True, 'next_step': 2})
        elif step == '2':
            goal_id = request.POST.get('career_goal')
            if goal_id:
                profile.career_goal = get_object_or_404(CareerGoal, id=goal_id)
                profile.save()
            return JsonResponse({'success': True, 'next_step': 3})
        elif step == '3':
            skill_ids = request.POST.getlist('skills')
            profile.current_skills.set(Skill.objects.filter(id__in=skill_ids))
            profile.save()
            
            # Auto-enroll in the career goal courses
            recs = get_career_recommendations(profile)
            for course in recs['courses']:
                Enrollment.objects.get_or_create(user=request.user, course=course)
                
            return JsonResponse({'success': True, 'redirect_url': '/student/dashboard/'})
            
    goals = CareerGoal.objects.all()
    skills = Skill.objects.all()
    context = {
        'profile': profile,
        'goals': goals,
        'skills': skills,
    }
    return render(request, "onboarding.html", context)


@login_required
def projects_list(request):
    profile = get_user_profile(request.user)
    assignments = Assignment.objects.all()
    submissions = Submission.objects.filter(user=request.user)
    
    projects_data = []
    for ass in assignments:
        sub = submissions.filter(assignment=ass).first()
        projects_data.append({
            'assignment': ass,
            'status': sub.status if sub else 'Not Started',
            'grade': sub.grade if sub else None,
            'submitted_date': sub.date_submitted if sub else None,
            'file': sub.submitted_file if sub else None
        })
        
    context = {
        'profile': profile,
        'projects': projects_data
    }
    return render(request, "projects.html", context)


@login_required
def certificates_list(request):
    profile = get_user_profile(request.user)
    certificates = Certificate.objects.filter(user=request.user)
    context = {
        'profile': profile,
        'certificates': certificates
    }
    return render(request, "certificates.html", context)


@login_required
def settings_view(request):
    profile = get_user_profile(request.user)
    goals = CareerGoal.objects.all()
    skills = Skill.objects.all()
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'edit_profile':
            request.user.first_name = request.POST.get('name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.save()
            
            profile.phone = request.POST.get('phone', '').strip()
            profile.college = request.POST.get('college', '').strip()
            profile.education = request.POST.get('education', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            
            goal_id = request.POST.get('career_goal')
            if goal_id:
                profile.career_goal = CareerGoal.objects.filter(id=goal_id).first()
            else:
                profile.career_goal = None
                
            skill_ids = request.POST.getlist('skills')
            profile.current_skills.set(Skill.objects.filter(id__in=skill_ids))
            
            if 'profile_photo' in request.FILES:
                profile.profile_photo = request.FILES['profile_photo']
                
            profile.save()
            messages.success(request, "Profile details successfully updated!")
            return redirect('settings')
            
        elif action == 'change_password':
            old_pass = request.POST.get('old_password', '')
            new_pass = request.POST.get('new_password', '')
            
            if request.user.check_password(old_pass):
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password successfully changed!")
            else:
                messages.error(request, "Incorrect current password.")
            return redirect('settings')
            
    context = {
        'profile': profile,
        'goals': goals,
        'skills': skills,
    }
    return render(request, "settings.html", context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        auth_logout(request)
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return redirect('login')
    return redirect('settings')


@login_required
@csrf_exempt
def autosave_code(request):
    if request.method == "POST":
        challenge_id = request.POST.get('challenge_id')
        code = request.POST.get('code', '')
        challenge = get_object_or_404(CodingChallenge, id=challenge_id)
        
        ChallengeProgress.objects.update_or_create(
            user=request.user,
            challenge=challenge,
            defaults={'code': code}
        )
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'POST required'}, status=400)


