from datetime import datetime
from io import StringIO
from flask import Blueprint, Response, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView
import pandas as pd
from sqlalchemy import func, select


from ..models.model import Instructor, Question, Quiz, Student, Score
from ..utils.common import cache
from ..utils.db import db

bp = Blueprint("analytics", __name__, url_prefix="/api")


class AnalyticsAPI(MethodView): 
    init_every_request = False 
    decorators = [jwt_required()]
    
    @cache.cached(timeout=30)
    def get(self):
        data = {
            "total_quizzes" : Quiz.query.count(),
            "total_questions" : Question.query.count(),
            "student_count" : Student.query.count(),
            "instructor_count": Instructor.query.count()
        }
    
        
        return data

class StudentAnayticsAPI(MethodView):
    init_every_request = False 
    decorators = [jwt_required()]
    
    
    @cache.cached(timeout=30)
    def get(self, id: int):
        student: Student = Student.query.get_or_404(id)
        
        quizzes: list[Quiz] = [i.quiz for i in student.quiz_assignments]
        
        score_list = [Score.query.filter_by(quiz_id=i.id, user_id=id).all() for i in quizzes]
        
        print(student.quiz_assignments)
        print(score_list)
        
        data = {
            "count_quiz_taken": len(student.quiz_assignments),
            "avg_score":  4 
        }
        
        return data

class InstrutorsAnayticsAPI(MethodView):
    init_every_request = False 
    decorators = [jwt_required()]
    
    
    def get(self, id:int):
        inst: Instructor = Instructor.query.get_or_404(id)
        
            
        question_count = db.session.query(func.count(Question.id)).\
    join(Quiz).\
    filter(Quiz.created_by == id).\
    scalar()
        
        return {
            "total_quiz": Quiz.query.filter_by(created_by=id).count(),
            "total_questions": question_count or 0 
        } 


@jwt_required()
def export_csv():
    q = request.args.get('q')
    
    def get_all_quiz():
        query = select(Quiz)
        quizzes = db.session.scalars(query).all()

        quiz_data = [quiz.to_dict() for quiz in quizzes]

        df = pd.DataFrame(quiz_data)

        csv_buffer = StringIO()

        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        response = Response(
            csv_buffer.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=quizzes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )

        return response

    def get_quiz_score_by_student(quiz_id):
        user_id = get_jwt_identity()
        
        quiz: Quiz = Quiz.query.get_or_404(quiz_id)
        score: list[Score] = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id)
    
        data = {"quiz_scores": 
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
        }

        quiz_scores_flat = []
        for score in data["quiz_scores"]:
            for question in score["questions"]:
                quiz_scores_flat.append({
                    "quiz_id": score["id"],
                    "question_id": question["id"],
                    "question": question["question"],
                    "correct": question["correct"],
                    "total_scored": score["total_scored"],
                    "date": score["date"],
                    "marks": score["marks"]
                })

        df = pd.DataFrame(quiz_scores_flat)
        
        csv_buffer = StringIO()

        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        response = Response(
            csv_buffer.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=quizzes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )

        return response

    match q:
        case "a_quiz":
           return get_all_quiz()
       
        case "s_quiz_score":
           quiz_id = request.args.get("quiz_id")    
           return get_quiz_score_by_student(quiz_id)
       
    return {"msg": "Nothing Found"}, 400


# Routes
bp.add_url_rule("/admin/analytics", view_func=AnalyticsAPI.as_view("analytics_api"))
bp.add_url_rule("/students/<int:id>/analytics", view_func=StudentAnayticsAPI.as_view("students_analytics_api"))
bp.add_url_rule("/instructors/<int:id>/analytics", view_func=InstrutorsAnayticsAPI.as_view("instr_analytics_api"))
bp.route("/export-csv", methods=['POST'])(export_csv)