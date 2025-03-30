from datetime import timedelta
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate
from flask.views import MethodView
from celery import Task, shared_task 

from backend.utils.db import db 
from ..utils.mail import mail, EmailMessage
from ..models.model import Question, Quiz, QuizAssignment, Score, Student
from backend.utils.common import add_db, do_commit, cache

bp = Blueprint("students", __name__, url_prefix="/api")


class StudentsAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    def get(self):
        return [i.to_dict() for i in Student.query.all()], 200


class SingleStudentAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    
    def get(self, id):
        return Student.query.get_or_404(id).to_dict(), 200

    def delete(self,id):
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        return do_commit("Student deleted successfully", "Student could not be deleted")

def accept_quiz(id:int):
    quiz_id: int | None = request.args.get("q_id", type=int)
    
    student: Student = Student.query.get_or_404(id)
    quiz: Quiz = Quiz.query.get_or_404(quiz_id)
    qass: QuizAssignment = QuizAssignment(student=student, quiz=quiz)

    reminder_time = quiz.date_of_quiz - timedelta(minutes=10)
    
    # print(quiz.date_of_quiz)
    
    # send_quiz_reminder("jashmevada@gmail.com", quiz.to_dict())
    send_quiz_reminder.apply_async(
        args=["jashmevada@gmail.com", quiz.to_dict()],
        eta=reminder_time
    )

    msg,c1 = add_db([qass])
    
    if quiz_id and c1 == 200:
        student.accept_quiz(quiz_id)
        return do_commit()
    
    return {'msg': 'No Quiz ID'}, 400 


@jwt_required()
def get_student_quizzes(id: int):
    student: Student = Student.query.get_or_404(id)
    quiz_set = []

    for i in student.quiz_assignments:
        if i.accepted:
            quiz_set.append(i)
            
    return [i.quiz.to_dict() for i in quiz_set]


@cache.cached(timeout=30)
@jwt_required()
def get_quizzes_score(id: int, quiz_id: int):
    # student: Student = Student.query.get_or_404(id)
    quiz: Quiz = Quiz.query.get_or_404(quiz_id)
    score: list[Score] = Score.query.filter_by(quiz_id=quiz_id, user_id=id)
    
    return {"quiz_scores": 
            [{
            "id": i.id,
            "questions": [{"id": j['question_id'],"question": Question.query.get_or_404(j['question_id']).question_statement, "correct": Question.query.get_or_404(j['question_id']).correct_option == int(j['selected_option'])} for j in i.selected_options],
            "total_scored": i.total_scored,
            "date": i.time_stamp_of_attempt,
            "marks": i.marks,

            } for i in score],
             
            "quiz_info":  {
                "chapter": quiz.chapter.name,
                "subject": quiz.chapter.subject.name,
                "department": quiz.chapter.subject.Sdepartment.title,
                "no_of_attmept": score.count(),
                "total_questions": len(quiz.questions)
            }
        }, 200 

@shared_task
def send_quiz_reminder(student_email, quiz_info):
    with current_app.app_context():
        msg = EmailMessage("Quiz Reminder",
                      from_email="noreply@quizapp.com",
                      to=[student_email])
        msg.body = f"Reminder: Your quiz '{quiz_info['title']}' starts in 30 minutes!"
        # mail.send_mail(msg)
        msg.send(fail_silently=False)
        # msg = EmailMessage("Quiz Reminder")
# Routes
bp.add_url_rule("/students", view_func=StudentsAPI.as_view("students_api"))
bp.add_url_rule("/students/<int:id>", view_func=SingleStudentAPI.as_view("single_student_api"))
bp.route("/students/<int:id>/quizzes", methods=["GET"])(get_student_quizzes)
bp.route("/students/<int:id>/quizzes/<int:quiz_id>/scores", methods=['GET'])(get_quizzes_score)
bp.route("/students/<int:id>/accept_quiz")(accept_quiz)