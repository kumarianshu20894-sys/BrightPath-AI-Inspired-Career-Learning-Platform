import os
from django.db import transaction
from BrightPath.models import Skill, CareerGoal, Course, Module, CodingChallenge, Quiz, Question, Assignment

def seed_database_data():
    if Skill.objects.exists():
        print("Database already seeded.")
        return

    print("Seeding database data...")
    with transaction.atomic():
        # 1. Create Skills
        skills_list = [
            "HTML", "CSS", "JavaScript", "Bootstrap", "Python", 
            "Django", "Flask", "SQL", "Git", "GitHub", "React", "Java", "C++"
        ]
        skills = {}
        for skill_name in skills_list:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skills[skill_name] = skill

        # 2. Create Career Goals
        career_goals_data = [
            {
                "name": "Python Developer",
                "description": "Build high-performance, scalable web apps and automations using Python, Django, and database integrations.",
                "skills": ["Python", "Django", "SQL", "Git", "GitHub"]
            },
            {
                "name": "Frontend Developer",
                "description": "Design and build beautiful, interactive, responsive web applications using HTML, CSS, JavaScript, Bootstrap, and React.",
                "skills": ["HTML", "CSS", "JavaScript", "Bootstrap", "React", "Git", "GitHub"]
            },
            {
                "name": "Backend Developer",
                "description": "Write servers, APIs, databases, and business logic using Python, Java, SQL, Django, and Git.",
                "skills": ["Python", "Django", "SQL", "Git", "GitHub", "Java"]
            },
            {
                "name": "Full Stack Developer",
                "description": "Become a complete developer managing front-end layouts and back-end logic, APIs, and databases.",
                "skills": ["HTML", "CSS", "JavaScript", "Bootstrap", "React", "Python", "Django", "SQL", "Git", "GitHub"]
            },
            {
                "name": "Data Analyst",
                "description": "Gather, clean, analyze, and visualize data using Python scripting, SQL queries, and visual tools.",
                "skills": ["Python", "SQL", "Git"]
            },
            {
                "name": "AI Engineer",
                "description": "Build predictive models and utilize neural networks using Python, data engines, and Git/GitHub repository systems.",
                "skills": ["Python", "SQL", "Git", "GitHub"]
            },
            {
                "name": "Cyber Security",
                "description": "Protect systems and networks from digital attacks using script commands, Python networking, and SQL logging.",
                "skills": ["Python", "SQL", "Git"]
            },
            {
                "name": "DevOps Engineer",
                "description": "Automate developer workflows, CI/CD, and server integrations using Python, Git, and version control.",
                "skills": ["Python", "Git", "GitHub"]
            },
            {
                "name": "Cloud Engineer",
                "description": "Design, deploy, and scale application cloud infrastructures, integrating SQL databases and Git pipelines.",
                "skills": ["Python", "SQL", "Git"]
            },
            {
                "name": "Java Developer",
                "description": "Design enterprise software, APIs, and desktop backends using Java OOP principles, C++ integrations, and SQL databases.",
                "skills": ["Java", "SQL", "Git", "GitHub", "C++"]
            }
        ]

        goals = {}
        for goal_data in career_goals_data:
            goal, _ = CareerGoal.objects.get_or_create(
                name=goal_data["name"],
                defaults={"description": goal_data["description"]}
            )
            for skill_name in goal_data["skills"]:
                goal.required_skills.add(skills[skill_name])
            goals[goal_data["name"]] = goal

        # 3. Create Courses
        courses_data = [
            {
                "title": "Python Development Masterclass",
                "description": "Start from absolute scratch with Python, master variables, control structures, and Object-Oriented Programming (OOP). Move on to SQLite database integrations, Git, and build complete dynamic web systems with Django.",
                "duration": "8 Weeks",
                "difficulty": "Beginner",
                "prerequisites": "None. Perfect for beginners.",
                "learning_outcomes": "Understand Python syntax, implement OOP design patterns, manipulate relational databases via SQLite and Django ORM, and build complete database CRUD applications with user authentication.",
                "career_goal": "Python Developer",
                "skills": ["Python", "Django", "SQL", "Git", "GitHub"],
                "modules": [
                    {
                        "title": "Python Basics & Object-Oriented Programming (OOP)",
                        "order": 1,
                        "theory": "Python is a high-level, interpreted programming language known for its readability. It supports multiple programming paradigms, including structured, procedural, and object-oriented programming.\n\nIn OOP, we organize code into 'Classes' and 'Objects'. A class is a blueprint, while an object is an instance. Important pillars of OOP include:\n- Inheritance: Creating a child class that inherits methods and properties of a parent class.\n- Polymorphism: Defining methods in child classes that have the same name as parent class methods but different logic.\n- Encapsulation: Hiding internal data and restricting direct access.\n- Abstraction: Displaying only essential details and hiding complexity.",
                        "code_examples": "# Basic variables and loops\nname = 'BrightPath'\nfor char in name:\n    print(char)\n\n# OOP Example\nclass Student:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def study(self):\n        return f'{self.name} is studying Python.'\n\nstudent1 = Student('Alice', 22)\nprint(student1.study())",
                        "official_documentation": "Python Official Documentation: https://docs.python.org/3/\nOOP in Python guide: https://realpython.com/python3-object-oriented-programming/",
                        "practice_problems": "1. Write a function to check if a number is prime.\n2. Write a class representing a Rectangle with area and perimeter methods.",
                        "challenges": [
                            {
                                "title": "Prime Number Checker",
                                "description": "Write a function `is_prime(n)` that returns `True` if a given number `n` is prime, and `False` otherwise.",
                                "difficulty": "Easy",
                                "xp": 10,
                                "time_estimate": "10 mins",
                                "input_format": "Integer n",
                                "output_format": "Boolean (True/False)",
                                "starter_code": "def is_prime(n):\n    # Write your code here\n    pass",
                                "hints": "A prime number is a positive integer greater than 1 that has no positive divisors other than 1 and itself. You can loop from 2 to the square root of n.",
                                "expected_output": "True",
                                "solution": "def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True"
                            },
                            {
                                "title": "Palindrome Checker",
                                "description": "Write a function `is_palindrome(s)` that returns `True` if the string `s` is a palindrome (reads the same forward and backward, ignoring case and spacing), and `False` otherwise.",
                                "difficulty": "Easy",
                                "xp": 10,
                                "time_estimate": "10 mins",
                                "input_format": "String s",
                                "output_format": "Boolean (True/False)",
                                "starter_code": "def is_palindrome(s):\n    # Write your code here\n    pass",
                                "hints": "Convert string to lowercase, remove non-alphanumeric characters, and check if it is equal to its reverse.",
                                "expected_output": "True",
                                "solution": "def is_palindrome(s):\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    return cleaned == cleaned[::-1]"
                            }
                        ],
                        "quiz": {
                            "title": "Python OOP Quiz",
                            "xp": 20,
                            "questions": [
                                {
                                    "text": "Which keyword is used to define a function in Python?",
                                    "o1": "func", "o2": "define", "o3": "def", "o4": "function", "correct": 3
                                },
                                {
                                    "text": "What is the purpose of __init__ in a Python class?",
                                    "o1": "To destroy objects", "o2": "To initialize the object attributes", "o3": "To inheritance methods", "o4": "To import packages", "correct": 2
                                },
                                {
                                    "text": "Which pillar of OOP refers to inheritance of properties?",
                                    "o1": "Polymorphism", "o2": "Encapsulation", "o3": "Inheritance", "o4": "Abstraction", "correct": 3
                                }
                            ]
                        },
                        "assignment": {
                            "title": "Design a OOP Bank Account System",
                            "description": "Create a Python file containing a class `BankAccount` with attributes `owner` and `balance` (defaulting to 0). Implement methods `deposit(amount)` and `withdraw(amount)`. Ensure that a withdrawal cannot exceed the available balance. Test it by performing multiple transactions. Submissions must be a single python file (.py) or a zip folder.",
                            "xp": 30
                        }
                    },
                    {
                        "title": "Databases, SQL & SQLite Integration",
                        "order": 2,
                        "theory": "Relational database management systems (RDBMS) store data in tabular tables with columns and rows. SQL (Structured Query Language) is the language used to communicate with databases.\n\nSQLite is a lightweight, serverless relational database engine built right into Python. To use it, we import the `sqlite3` module. The core workflow is:\n1. Establish connection: `conn = sqlite3.connect('dbname.db')`\n2. Create a cursor object: `cursor = conn.cursor()`\n3. Execute SQL statements: `cursor.execute('SELECT * FROM users')`\n4. Commit transactions: `conn.commit()`\n5. Close connection: `conn.close()`",
                        "code_examples": "import sqlite3\n\n# Create a database in memory\nconn = sqlite3.connect(':memory:')\ncursor = conn.cursor()\n\n# Create table\ncursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')\n\n# Insert user\ncursor.execute(\"INSERT INTO users (name, age) VALUES ('Alice', 22)\")\nconn.commit()\n\n# Query database\ncursor.execute('SELECT * FROM users')\nprint(cursor.fetchall())\nconn.close()",
                        "official_documentation": "SQLite Python Docs: https://docs.python.org/3/library/sqlite3.html\nSQL SELECT Tutorial: https://www.w3schools.com/sql/sql_select.asp",
                        "practice_problems": "1. Write SQL to select all users whose names start with 'A'.\n2. Write python script to delete duplicate rows based on email.",
                        "challenges": [
                            {
                                "title": "Even Odd Numbers",
                                "description": "Write a function `even_odd(n)` that returns the string 'Even' if `n` is even, and 'Odd' if `n` is odd.",
                                "difficulty": "Easy",
                                "xp": 10,
                                "time_estimate": "5 mins",
                                "input_format": "Integer n",
                                "output_format": "String ('Even' or 'Odd')",
                                "starter_code": "def even_odd(n):\n    # Write your code here\n    pass",
                                "hints": "Use the modulo operator `%`. An even number divided by 2 has a remainder of 0.",
                                "expected_output": "Even",
                                "solution": "def even_odd(n):\n    return 'Even' if n % 2 == 0 else 'Odd'"
                            }
                        ],
                        "quiz": {
                            "title": "SQL & SQLite Quiz",
                            "xp": 20,
                            "questions": [
                                {
                                    "text": "Which SQL command is used to add new data to a table?",
                                    "o1": "ADD DATA", "o2": "INSERT INTO", "o3": "UPDATE", "o4": "CREATE", "correct": 2
                                },
                                {
                                    "text": "Which SQLite command fetches all database queries into a list of tuples?",
                                    "o1": "cursor.fetch()", "o2": "cursor.readall()", "o3": "cursor.fetchall()", "o4": "cursor.get()", "correct": 3
                                }
                            ]
                        },
                        "assignment": {
                            "title": "SQLite Student Management System",
                            "description": "Write a Python script that creates a SQLite database 'school.db'. Create a table 'students' with fields id, name, grade, and age. Add functions to: add_student, view_students, update_student_grade, and delete_student. Submit the code in a single Python file (.py).",
                            "xp": 30
                        }
                    },
                    {
                        "title": "Django MVT Architecture & CRUD Setup",
                        "order": 3,
                        "theory": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.\n\nIt follows the MVT (Model-View-Template) architectural pattern:\n- Model: Defines database schema and handles data access. Django ORM automatically maps models to SQL tables.\n- View: Contains application logic. It receives HTTP requests, interacts with Models, and returns HTTP responses (often rendering a Template).\n- Template: A text file (usually HTML) that determines the visual layout, using Django Template Language (DTL) to dynamically inject data.",
                        "code_examples": "# Models.py definition\nfrom django.db import models\n\nclass Task(models.Model):\n    title = models.CharField(max_length=100)\n    completed = models.BooleanField(default=False)\n\n# Views.py definition\nfrom django.shortcuts import render\nfrom .models import Task\n\ndef task_list(request):\n    tasks = Task.objects.all()\n    return render(request, 'tasks.html', {'tasks': tasks})",
                        "official_documentation": "Django Official Docs: https://docs.djangoproject.com/en/stable/\nDjango MVT Introduction: https://www.geeksforgeeks.org/django-mvt-architecture/",
                        "practice_problems": "1. Write a view that takes a student ID and displays their details.\n2. Write a templates block utilizing template inheritance.",
                        "challenges": [
                            {
                                "title": "Factorial Calculator",
                                "description": "Write a recursive or iterative function `factorial(n)` that returns the factorial of non-negative integer `n`.",
                                "difficulty": "Medium",
                                "xp": 15,
                                "time_estimate": "15 mins",
                                "input_format": "Integer n",
                                "output_format": "Integer",
                                "starter_code": "def factorial(n):\n    # Write your code here\n    pass",
                                "hints": "Factorial of 5 (5!) is 5 * 4 * 3 * 2 * 1 = 120. Factorial of 0 is 1.",
                                "expected_output": "120",
                                "solution": "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"
                            }
                        ],
                        "quiz": {
                            "title": "Django Core Quiz",
                            "xp": 20,
                            "questions": [
                                {
                                    "text": "What is Django's default object-relational mapper called?",
                                    "o1": "Django SQL", "o2": "Django ORM", "o3": "Django DB", "o4": "SQLAlchemy", "correct": 2
                                },
                                {
                                    "text": "Which file is responsible for routing URL paths to views?",
                                    "o1": "settings.py", "o2": "models.py", "o3": "urls.py", "o4": "views.py", "correct": 3
                                }
                            ]
                        },
                        "assignment": {
                            "title": "Simple Django CRUD Application",
                            "description": "Create a Django project that manages a 'Product' model (name, price, stock). Implement a view to list all products and a form to add a product. Compress the project (excluding venv and db.sqlite3) into a ZIP and submit.",
                            "xp": 30
                        }
                    }
                ]
            },
            {
                "title": "Modern Frontend Fundamentals",
                "description": "Learn modern frontend engineering using HTML5, CSS3, CSS Flexbox & Grid layout designs, and interactive JavaScript. Advance to UI frameworks using Bootstrap 5 and Single-Page App concepts with React.",
                "duration": "6 Weeks",
                "difficulty": "Beginner",
                "prerequisites": "None.",
                "learning_outcomes": "Build completely responsive web pages, create rich client interactions, build layouts with Bootstrap 5 components, and understand React components and state properties.",
                "career_goal": "Frontend Developer",
                "skills": ["HTML", "CSS", "JavaScript", "Bootstrap", "React", "Git", "GitHub"],
                "modules": [
                    {
                        "title": "HTML5, CSS3 & Layout Flexbox/Grid",
                        "order": 1,
                        "theory": "HTML5 represents the structure, using semantic tags like <header>, <section>, <article>, and <footer> to increase SEO and accessibility.\n\nCSS3 handles visual presentation. Flexbox (flexible box layout) handles one-dimensional grids (aligned rows or columns). CSS Grid is a two-dimensional layout system that handles rows and columns concurrently. Media queries form the core of Responsive Web Design, altering CSS based on browser viewport size (e.g. `@media (max-width: 768px)`).",
                        "code_examples": "/* Flexbox Centering */\n.parent {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    height: 100vh;\n}\n\n/* Grid Layout */\n.grid-container {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));\n    gap: 20px;\n}",
                        "official_documentation": "HTML Semantic: https://www.w3schools.com/html/html5_semantic_elements.asp\nCSS Flexbox: https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
                        "practice_problems": "1. Build a responsive navbar using only HTML and CSS.\n2. Align 3 panels with equal width spacing using CSS grid.",
                        "challenges": [
                            {
                                "title": "Fibonacci Sequence",
                                "description": "Write a function `fibonacci(n)` that returns the `n`th number in the Fibonacci sequence (where fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, etc.).",
                                "difficulty": "Medium",
                                "xp": 15,
                                "time_estimate": "12 mins",
                                "input_format": "Integer n",
                                "output_format": "Integer",
                                "starter_code": "def fibonacci(n):\n    # Write your code here\n    pass",
                                "hints": "Fibonacci formula: F(n) = F(n-1) + F(n-2). You can use iteration with variables a and b initialized to 0 and 1.",
                                "expected_output": "5",
                                "solution": "def fibonacci(n):\n    if n <= 0: return 0\n    if n == 1: return 1\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b"
                            }
                        ],
                        "quiz": {
                            "title": "HTML5 & CSS3 Quiz",
                            "xp": 20,
                            "questions": [
                                {
                                    "text": "Which HTML5 element is used to describe an independent, self-contained article layout?",
                                    "o1": "<section>", "o2": "<article>", "o3": "<aside>", "o4": "<div>", "correct": 2
                                },
                                {
                                    "text": "What is the CSS property to change the space inside elements between border and text?",
                                    "o1": "margin", "o2": "border-width", "o3": "padding", "o4": "spacing", "correct": 3
                                }
                            ]
                        },
                        "assignment": {
                            "title": "Responsive Product Landing Page",
                            "description": "Develop a responsive product landing page using only HTML5 semantic elements and CSS3 (Flexbox/Grid allowed). Include a feature list, testimonial cards, and a signup form. Save as index.html and style.css in a ZIP and upload.",
                            "xp": 30
                        }
                    }
                ]
            }
        ]

        for course_data in courses_data:
            goal = goals[course_data["career_goal"]]
            course, _ = Course.objects.get_or_create(
                title=course_data["title"],
                defaults={
                    "description": course_data["description"],
                    "duration": course_data["duration"],
                    "difficulty": course_data["difficulty"],
                    "prerequisites": course_data["prerequisites"],
                    "learning_outcomes": course_data["learning_outcomes"],
                    "career_goal": goal
                }
            )
            for skill_name in course_data["skills"]:
                course.skills.add(skills[skill_name])

            # Modules
            for mod_data in course_data["modules"]:
                module, _ = Module.objects.get_or_create(
                    course=course,
                    title=mod_data["title"],
                    defaults={
                        "order": mod_data["order"],
                        "theory": mod_data["theory"],
                        "code_examples": mod_data["code_examples"],
                        "official_documentation": mod_data["official_documentation"],
                        "practice_problems": mod_data["practice_problems"]
                    }
                )

                # Coding Challenges
                for chal_data in mod_data.get("challenges", []):
                    CodingChallenge.objects.get_or_create(
                        module=module,
                        title=chal_data["title"],
                        defaults={
                            "description": chal_data["description"],
                            "difficulty": chal_data["difficulty"],
                            "xp": chal_data["xp"],
                            "time_estimate": chal_data["time_estimate"],
                            "input_format": chal_data["input_format"],
                            "output_format": chal_data["output_format"],
                            "starter_code": chal_data["starter_code"],
                            "hints": chal_data["hints"],
                            "expected_output": chal_data["expected_output"],
                            "solution": chal_data["solution"]
                        }
                    )

                # Quiz
                quiz_data = mod_data.get("quiz")
                if quiz_data:
                    quiz, _ = Quiz.objects.get_or_create(
                        module=module,
                        defaults={
                            "title": quiz_data["title"],
                            "xp": quiz_data["xp"]
                        }
                    )
                    for q_data in quiz_data["questions"]:
                        Question.objects.get_or_create(
                            quiz=quiz,
                            text=q_data["text"],
                            defaults={
                                "option1": q_data["o1"],
                                "option2": q_data["o2"],
                                "option3": q_data["o3"],
                                "option4": q_data["o4"],
                                "correct_option": q_data["correct"]
                            }
                        )

                # Assignment
                assign_data = mod_data.get("assignment")
                if assign_data:
                    Assignment.objects.get_or_create(
                        module=module,
                        defaults={
                            "title": assign_data["title"],
                            "description": assign_data["description"],
                            "xp": assign_data["xp"]
                        }
                    )

    print("Database seeding completed.")
