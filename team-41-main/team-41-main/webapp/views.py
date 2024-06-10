from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from learning import Learning


def index(request):
    return render(request, "index.html")


def inputSkill(request):
    return render(request, "inputSkill.html")


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def inputSkill(request: HttpRequest) -> HttpResponse:
    return render(request, "inputSkill.html")


def showKnownSkillsForm(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    target_skill = request.GET["skill"]
    interests = request.GET["interests"]
    app.save_interests(interests)
    skill_tree = app.create_skill_tree(target_skill)
    dependencies = sorted(set(skill_tree.skills_to_dependencies.keys()))
    return render(request, 'knownSkillsForm.html', {'content': dependencies})


def roadmap(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    updated_skills = request.POST.getlist('skills')
    if updated_skills:
        app.save_known_skills(updated_skills)
    roadmap = app.get_roadmap()
    return render(request, 'roadmap.html', {'content': roadmap})


def theory(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    target_skill = request.GET["skill"]
    learning_material = app.load_theory(target_skill)['learning_material']
    return render(request, 'theory.html', {'learning_material': learning_material, 'skill': target_skill})


def quiz(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    target_skill = request.GET["skill"]
    question_number = int(request.GET.get('question', 1))
    answer = request.POST.get('answer')
    print(list(request.POST.items()))
    questions = app.load_theory(target_skill)['questions']
    

    if answer:
        previous = questions[question_number - 2]
        correct_number = str(previous['answer'])
        correct = answer == correct_number
        correct_answer = previous['options'][int(correct_number) - 1]
        print(f"Correct: {correct}, correct number: {correct_number}, correct answer: {correct_answer}")
    else:
        correct = None
        correct_number = None
        correct_answer = None
        print('None')

    if question_number <= len(questions):
        quiz = questions[question_number - 1]
    else:
        quiz = None

    return render(request, 'quiz.html', {'quiz': quiz, 'skill': target_skill, 'question_number': question_number, 'correct': correct, 'correct_number': correct_number, 'correct_answer': correct_answer})


def task(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    target_skill = request.GET["skill"]
    task = app.load_task(target_skill)
    return render(request, 'task.html', {'task': task, 'skill': target_skill})


def checkTask(request: HttpRequest) -> HttpResponse:
    app = Learning(request.session, 'HTML')
    target_skill = request.GET["skill"]
    print(request.FILES)
    code = request.FILES['file'].read().decode('utf-8')
    print(code)

    feedback = app.feedback_data(target_skill, code)
    return render(request, 'feedback.html', {'feedback': feedback, 'skill': target_skill})