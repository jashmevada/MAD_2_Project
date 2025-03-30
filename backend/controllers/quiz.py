from datetime import datetime, timedelta
from time import sleep
import uuid
from flask import Blueprint, Response, current_app, json, jsonify, request, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.model import  Quiz, Question, Score, TimerSession, User
from backend.models.schema import QuizAttempt, QuizCreateModel, QuizQueryModel
from backend.utils.common import add_db, cache
from ..utils.db import db, redis_client

bp = Blueprint("quiz", __name__, url_prefix="/api")


class QuizAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    
    @cache.cached(timeout=30)
    @validate()
    def get(self, query: QuizQueryModel):
        if query.subject_id:
            return [i.to_dict() for i in Quiz.query.filter_by()]
        
        
        return [i.to_dict() for i in Quiz.query.all()], 200

    @validate()
    def post(self, body: QuizCreateModel):
        quiz = Quiz(**body.model_dump(exclude=["questions", 'subject_id']))

        for question in body.questions:
            quiz.questions.add(Question(
                question_statement=question.question_statement,
                options={i: option for i, option in enumerate(question.options)},
                correct_option=question.correct_option
            ))

        print(quiz)
        return add_db([quiz], "Sucess", "Failed")
  
class SingleQuizAPI(MethodView):
    init_every_request = False 
    decorators = [jwt_required()]
    
    def get(self, id:int):
        return Quiz.query.get_or_404(id).to_dict(), 200 

    @validate()
    def put(self, id: int, body: QuizCreateModel):
        quiz: Quiz = Quiz.query.get_or_404(id)
   
        for key, value in body.model_dump(exclude=["questions", 'subject_id']).items():
            setattr(quiz, key, value)
        
        quiz.questions.clear()
        
        for question in body.questions:
            quiz.questions.add(Question(
                question_statement=question.question_statement,
                options={i: option for i, option in enumerate(question.options)},
                correct_option=question.correct_option
            ))

        print(f"Quiz: {quiz.to_dict()} \n Questions: {[i.to_dict() for i in quiz.questions]}")
        return add_db([quiz], "Sucess", "Failed")
        
    
    def delete(self, id: int):
        quiz: Quiz = Quiz.query.get_or_404(id)

        try:
            db.session.delete(quiz)
            return {'msg': 'DELETED'}, 200
        except Exception as e:
            return {"error", f"{e}"}, 500
  

@jwt_required()
def get_questions(quiz_id):
    quiz: Quiz = Quiz.query.get_or_404(quiz_id)
    user_id = get_jwt_identity()
    # print(quiz.date_of_quiz)
    user: User = User.query.get_or_404(user_id)
    
    if quiz.date_of_quiz <= datetime.now():
        return [i.to_dict() for i in quiz.questions], 200
    elif user.role == 'admin' or user.role == 'instructor':
        return [i.to_dict() for i in quiz.questions], 200
    
    return {"error": "Quiz is not ready."}, 400 

# ------------------
      
def format_sse(data, event=None):
    msg = f"data: {json.dumps(data)}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg

# SSE endpoints
def timer_stream(quiz_id, user_id):
    """SSE endpoint that streams timer updates"""
    def generate():
        # Send initial connection established event
        yield format_sse({"status": "connected"}, event="connection")
        
        # Check if there's an active timer session
        timer_session: TimerSession = TimerSession.query.filter_by(
            quiz_id=quiz_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if timer_session:

            yield format_sse({
                "timer_session_id": timer_session.id,
                "time_remaining": timer_session.time_remaining,
                "duration": timer_session.duration_seconds
            }, event="timer_update")
            
            # Stream timer updates
            while True:
                # Re-fetch timer session to get latest state
                timer_session = TimerSession.query.filter_by(
                    id=timer_session.id
                ).first()
                
                if not timer_session or not timer_session.is_active:
                    # Timer session ended
                    yield format_sse({
                        "status": "completed",
                        "time_remaining": 0
                    }, event="timer_update")
                    break
                
                time_remaining = timer_session.time_remaining
                
                # Send timer update
                yield format_sse({
                    "timer_session_id": timer_session.id,
                    "time_remaining": time_remaining,
                    "duration": timer_session.duration_seconds
                }, event="timer_update")
                
                # If timer has expired, end the session
                if time_remaining <= 0:
                    timer_session.is_active = False
                    db.session.commit()
                    yield format_sse({
                        "status": "completed",
                        "time_remaining": 0
                    }, event="timer_update")
                    break
                
                sleep(1)
        else:
            # No active timer session
            yield format_sse({"status": "not_started"}, event="timer_status")
    
    response = Response(stream_with_context(generate()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"  # For Nginx
    return response

@jwt_required()
def start_timer(quiz_id):
    """Start a new timer for a quiz"""
    data = request.json
    user_id = data.get('user_id')
    duration = data.get('duration')  # in seconds
    
    if not all([quiz_id, user_id, duration]):
        return jsonify({"error": "Missing required parameters"}), 400
    

    existing_session : TimerSession = TimerSession.query.filter_by(
        quiz_id=quiz_id,
        user_id=user_id,
        is_active=True
    ).first()
    
    if existing_session:
        return jsonify({
            "timer_session_id": existing_session.id,
            "time_remaining": existing_session.time_remaining,
            "duration": existing_session.duration_seconds
        })
    

    session_id = str(uuid.uuid4())
    new_session = TimerSession(
        id=session_id,
        quiz_id=quiz_id,
        user_id=user_id,
        duration_seconds=duration,
        start_time=datetime.now(),
        is_active=True
    )
    msg,cd = add_db([new_session], "Timer session created", "Failed to create timer session")
    
    if cd != 200: 
        return jsonify({"error": msg}), cd
    
    redis_client.setex(
        f"quiz:timer:{session_id}",
        duration,  # TTL in seconds
        json.dumps({
            'quiz_id': quiz_id,
            'user_id': user_id,
            'start_time': new_session.start_time.isoformat(),
            'duration': duration
        })
    )
    
    return jsonify({
        "timer_session_id": session_id,
        "time_remaining": duration,
        "duration": duration
    })

@jwt_required()
def end_timer(quiz_id):
    """End a timer session"""
    data = request.json
    timer_session_id = data.get('timer_session_id')
    
    if not timer_session_id:
        return jsonify({"error": "Missing timer_session_id"}), 400
    
    # End the timer session
    timer_session = TimerSession.query.get(timer_session_id)
    if timer_session:
        timer_session.is_active = False
        db.session.commit()
        
        # Delete Redis key
        redis_client.delete(f"quiz:timer:{timer_session_id}")
        
        return jsonify({
            "success": True,
            "message": "Timer ended successfully"
        })
    
    return jsonify({"error": "Timer session not found"}), 404

@jwt_required()
def get_timer(timer_session_id):
    """Get the current time remaining for a timer session."""
    try:
        user_id = get_jwt_identity()
        
        # Try to get from Redis first (faster)
        redis_key = f"quiz:timer:{timer_session_id}"
        cached_timer = redis_client.get(redis_key)
        
        if cached_timer:
            timer_data = json.loads(cached_timer)
            start_time = datetime.fromisoformat(timer_data['start_time'])
            duration = timer_data['duration']
            
            now = datetime.now()
            end_time = start_time + timedelta(seconds=duration)
            
            if now >= end_time:
                time_remaining = 0
            else:
                time_remaining = int((end_time - now).total_seconds())
                
            return jsonify({'time_remaining': time_remaining})
        
        # If not in Redis, check the database
        timer_session = TimerSession.query.filter_by(
            id=timer_session_id,
            user_id=user_id
        ).first()
        
        if not timer_session:
            return jsonify({'error': 'Timer session not found'}), 404
            
        return jsonify({'time_remaining': timer_session.time_remaining})
        
    except Exception as e:
        current_app.logger.error(f"Error getting timer: {str(e)}")
        return jsonify({'error': str(e)}), 400

@jwt_required()
def save_answer(quiz_id):
    """Save an individual answer during the quiz."""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        timer_session = TimerSession.query.filter_by(
            quiz_id=quiz_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not timer_session or timer_session.time_remaining <= 0:
            return jsonify({'error': 'Quiz time has expired'}), 400
            
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        
        # Store in Redis for fast access and to handle potential submission at timeout
        redis_client.hset(
            f"quiz:answers:{quiz_id}:{user_id}",
            question_id,
            selected_option
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error saving answer: {str(e)}")
        return jsonify({'error': str(e)}), 401

@validate()
@jwt_required()
def submit_quiz(quiz_id, body: QuizAttempt):
    """Submit all answers and end the quiz."""
    try:
        
        user_id = get_jwt_identity()


        timer_session = TimerSession.query.filter_by(
            quiz_id=quiz_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if timer_session:
            timer_session.is_active = False
            db.session.commit()
            
            # Clear Redis timer
            redis_client.delete(f"quiz:timer:{timer_session.id}")

        quiz: Quiz = Quiz.query.get_or_404(quiz_id)
        quiz.no_student_attempt += 1
        
        score = Score(quiz_id=quiz_id, user_id=user_id, selected_options=body.answers)

        current_app.logger.info(add_db([score]))

        redis_client.delete(f"quiz:answers:{quiz_id}:{user_id}")
        
        return jsonify({'success': True, 'message': 'Quiz submitted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error submitting quiz: {str(e)}")
        return jsonify({'error': str(e)}), 400

# API Routes 
bp.add_url_rule("/quizzes", view_func=QuizAPI.as_view("quiz_api"))
bp.add_url_rule("/quizzes/<int:id>", view_func=SingleQuizAPI.as_view("single_quiz_api"))
bp.route("/quizzes/<int:quiz_id>/questions")(get_questions)

bp.route('/quizzes/timer/<int:timer_session_id>', methods=['GET'])(get_timer)
bp.route('/quizzes/<int:quiz_id>/end-timer', methods=['POST'])(end_timer)
bp.route('/quizzes/<int:quiz_id>/start-timer', methods=['POST'])(start_timer)
bp.route('/quizzes/<int:quiz_id>/timer-stream/<int:user_id>')(timer_stream)
bp.route('/quizzes/<int:quiz_id>/save-answer', methods=['POST'])(save_answer)
bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])(submit_quiz)
