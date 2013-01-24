# Author : Diederik Beker
# Descrp : Contains controller logic for the answer choice
# Changes:
# Comment:

from flask import render_template, g, request, abort, redirect
from models.question import Question
from models.answer import AnswerModel
from models.answerchoice import AnswerChoiceModel
from models import answer
from dbconnection import session
from random import randrange

class Answerchoice():
    def __init__(self, request):        
        # lele add dummy questions le
        if len(Question.get_all()) == 0:
            userID = g.lti.get_user_id()
            q1 = Question("1","1","What am I?",True,1000)
            q2 = Question("2","1","Who am I?",True,1000)
            q3 = Question("3","1","Where am I?",True,1000)
            session.add(q1)
            session.add(q2)
            session.add(q3)
            a11 = AnswerModel("einseins",1,userID,0)
            a12 = AnswerModel("einszwei",1,1338,0)
            a13 = AnswerModel("einsdrei",1,1339,0)
            a21 = AnswerModel("zweieins",2,userID,0)
            a22 = AnswerModel("zweizwei",2,1338,0)
            a23 = AnswerModel("zweidrei",2,1339,0)
            a31 = AnswerModel("dreieins",3,userID,0)
            a32 = AnswerModel("dreizwei",3,1338,0)
            a33 = AnswerModel("dreidrei",3,1339,0)
            session.add(a11)
            session.add(a12)
            session.add(a13)
            session.add(a21)
            session.add(a22)
            session.add(a23)
            session.add(a31)
            session.add(a32)
            session.add(a33)
            session.commit()

    def render(self):
        questionID = request.values['questionid']
        if question_valid(questionID):
            return render_template('choice.html',question=Question.by_id[questionID], answer1=AnswerModel.by_id(request.values['answerid1']), answer2=AnswerModel.by_id(request.values['answerid2']))
        else:
            return render_template('/choicelobby')
        

    def randpop(array):
        return array.pop(randrange(0,len(array)))
        
    def getotheranswers(self,userid,questionid):
        allanswers = (AnswerModel.get_all())
        validAnswers = []
        for current in allanswers:
            if current.userID != userID and current.questionID == questionID:
                validAnswers.append(current)
    
    def process(self):
        userid = g.lti.get_user_id()

        try:
            answer0 = int(request.values['answerzero'])
            answer1 = int(request.values['answerone'])
            bestanswer = int(request.values['bestanswer'])
        except KeyError:
            return abort(404)
        except ValueError:
            return abort(404)
        
        if answer0 == bestanswer:
            best = answer0
            other = answer1
        elif answer1 == bestanswer:
            best = answer1
            other = answer0
        else:
            return 404
        
        try:
            session.add(AnswerChoiceModel(userid,best,other))
            session.commit()
        except:
            session.rollback()

        return 'success' 

    def lobby(self):
        userID = g.lti.get_user_id()
        questionID = int(request.values['question_id'])
        validAnswers = getotheranswers(userID,questionID)
        
        if len(validAnswers) < 2:
            return render_template('choicelobby.html',question='DUMMY')
        else:
            return redirect('/answerchoice?questionid='+str(questionID)+'&answerid1='+str(randpop(validAnswers))+'&answerid2='+str(randpop(validAnswers)))