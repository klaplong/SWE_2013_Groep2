from models.rating import AnswerRating, Rating
from models.answer import AnswerModel
from flask import render_template, session as fsession

class AssignRatings():
    def __init__(self, answer_id):
        self.answer = AnswerModel.by_id(answer_id)
        if self.answer == None:
            self.answer = "Error no answer found"

        fsession['assignrating'] = str(answer_id)
    
    @staticmethod
    def assign(request):
        for rating_id in request.form.getlist('rating'):
            AnswerRating.add_answerrating(fsession['assignrating'], rating_id)
              
    def render(self):
        return render_template('ratings.html', answer=self.answer,
                               ratings=Rating.get_all())
