from models import answer, question
from flask import render_template, g
import datetime
import sqlalchemy.orm.exc as sqlalchemyExp


class Answer():
    def __init__(self, request):
        self.request = request

    def render(self):
        # dummy shit, get some real data
        qText = 'wat is het antwoord op deze dummy vraag?'
        uID = 19#g.lti.get_user_id()
        qID = -1
        timerD = 10
        timerDstr = "00:10"

        # Post should be real data
        if self.request.method == 'POST' and 'questionID' in self.request.form:
            try:
                qID = int(self.request.form['questionID'])
                qText = question.Question.by_id(qID).question
            except(sqlalchemyExp.NoResultFound):
                pass
            except Exception as e:
                return e

        if 'answerText' in self.request.form:
            # save answer
            answerText = self.request.form['answerText']
            aID = answer.AnswerModel.getAnswerID(uID, qID)

            flag = "false"
            if self.timeLeft(aID, timerD, 0):
                answer.AnswerModel.updateAnswer(aID, answerText)
                flag = "true"

            return render_template('answersaved.html', flag=flag)

        elif 'showall' in self.request.form:
            # Render all
            return self.render_all()
        elif 'viewanswer' in self.request.form:
            # show answer
            aid = int(self.request.form['id'])
            return render_template('editanswer.html', answer=answer.AnswerModel.by_id(aid))
        elif 'reviewAnswer' in self.request.form:
            # save review answer
            questionID = int(self.request.form['questionID'])
            userID = self.request.form['userID']
            reviewAnswer = self.request.form['reviewAnswer']
            edit = int(self.request.form['edit'])
            answer.AnswerModel.savereview(
                questionID, userID, reviewAnswer, edit)
            return render_template('answersaved.html', flag='true')
        elif 'removeAnswer' in self.request.form:
            id = int(self.request.form['id'])
            answer.AnswerModel.remove_by_id(id)
            return render_template('answersaved.html', flag='removed')
        else:
            if answer.AnswerModel.checkAnswerExist(uID, qID):
                aID = answer.AnswerModel.getAnswerID(uID, qID)
                if self.timeLeft(aID, timerD, 0):
                    return render_template('answer.html', questionID=qID, userID=uID, questionText=qText, timerDuration=self.timeLeft(aID, timerD, 1), go="true", answerID=aID)
                else:
                    return render_template('answer.html', questionID=qID, userID=uID, questionText=qText, timerDuration= timerDstr, go="false")
            else:
                answer.AnswerModel.save(qID, uID, "")
                return render_template('answer.html', questionID=qID, userID=uID, questionText=qText, timerDuration= timerDstr, go="true")

    def timeLeft(self, aID, timerD, giveTime):
        currentTime = datetime.datetime.now()
        timeAnswered = answer.AnswerModel.getTimeStamp(aID)
        difference = currentTime - timeAnswered
        seconds = difference.days * 86400 + difference.seconds

        if giveTime == 1:
            minutes = int((timerD - seconds) / 60)
            seconds = int((timerD - seconds) % 60)
            if minutes < 10:
                minutes = str("0"+str(minutes))
            else:
                minutes = str(minutes)
            if seconds < 10:
                seconds = str("0"+str(seconds))
            else:
                seconds = str(seconds)
            return minutes + ":" + seconds

        if seconds < timerD + 2:
            return True
        else:
            return False

    def render_filtered(self):
        postdata = self.request.form

        args = {}
        if self.request.method == "POST":
            if "questionID" in postdata and len(postdata["questionID"]) > 0:
                args["questionID"] = postdata["questionID"]
            if "userID" in postdata and len(postdata["userID"]) > 0:
                args["userID"] = postdata["userID"]
            if "id" in postdata and len(postdata["id"]) > 0:
                args["id"] = postdata["id"]

        return render_template('answerfilter.html', answers=answer.AnswerModel.get_filtered(**args))

    def render_all(self):
        # Render all
        return render_template('showanswers.html', answers=answer.AnswerModel.get_all())
