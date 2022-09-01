import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

# i got this from the bookshelf app in udacity, similar to paginate_books function
def paginate_questions(request, question):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in question]
    current_questions = questions[start:end]

    return current_questions



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def categories():
    categories = Category.query.all()
    
    try:
      # all_categories = []
      # for category in categories:
      #   all_categories.append(category.type)

      # the list predefined numbering was affecting my result in the categories/<int:category_id>/questions part 

      # a list works better
      all_categories = {}
      for category in categories:
        all_categories[category.id] = category.type

      return jsonify(
        {
          "success": True,
          "categories": all_categories,
          "total_categories": len(categories),
        }    
      )
    except:
      abort(405)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():  
      question = Question.query.order_by(Question.id).all()
      current_question = paginate_questions(request, question)

      categories = Category.query.order_by(Category.id).all()
      category_type = {}
      for category in categories:
        category_type[category.id] = category.type
    
      if len(current_question) == 0:
        abort(404)

      return jsonify(
        {
          "success": True,
          "questions": current_question,
          "total_questions": len(Question.query.all()),
          "current_category": None,
          "categories": category_type
        }
      )
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
    question = Question.query.filter(Question.id==question_id).one_or_none()
    
    if question is None:
      abort(422)

    else:
      try:
        question.delete()
 
        question = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, question)
        return jsonify({
          'success': True,
          'deleted': question_id,
          "questions": current_questions,
          "total_questions": len(Question.query.all()),
        })
      except:
        abort(422)
      
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=["POST"])
  def create_question():
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')

    try:
      question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_question = paginate_questions(request, selection)

      return jsonify(
        {
          "success": True,
          "created": question.id,
          "questions": current_question,
          "total_questions": len(Question.query.all()),
        }
      )

    except:
      abort(422)
  

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=["POST"])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    
    question = Question.query.filter(Question.question.ilike('%' + search_term + '%'))
    current_questions = paginate_questions(request, question)

    return jsonify(
      {
      "success" : True,
      "questions": current_questions,
      "total_questions": len(question.all()),
      "current_category": None
      }
    )
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def category_question(category_id):
    
    category = Category.query.filter_by(id=category_id).all()

    if not category:
      abort(404)
    
    else:
      try:
        questions = Question.query.filter(Question.category==category_id)
        current_questions = paginate_questions(request, questions)

        return jsonify({
          "success": True,
          "questions": current_questions,
          "total_questions": len(current_questions),
          "current_category": category_id
        })
      except:
        abort(422)
    
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def get_quiz_question():
    body = request.get_json()

    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category', 'id')
    category_id = quiz_category['id']
    questions = None

    if category_id == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category = category_id).all()
      
    new_questions = questions.copy()
    
    random.shuffle(new_questions)
    
    current_question = ''

    for question in new_questions:
      if previous_questions.count(question.id) == 0:
        current_question = question.format()
        break

    return jsonify({
      "success": True,
      "question": current_question
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def not_found(error):
        return (jsonify({"success": False, "error": 404, "message": "resource not found"}), 404)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422)


  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({"success": False, "error": 400, "message": "bad request"}), 400)

  @app.errorhandler(405)
  def not_found(error):
    return (jsonify({"success": False, "error": 405, "message": "method not allowed"}), 405)

  @app.errorhandler(500)
  def not_found(error):
        return (jsonify({"success": False, "error": 500, "message": "internal server error"}), 500)

  return app

    
