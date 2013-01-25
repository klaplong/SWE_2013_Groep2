# Author : Dexter Drupsteen
# Descrp : Contains routing and calling of the constrollers
# Changes:
# Comment: MultiDict with isinstructor,consumerkey,coursekey and coursename in
#          the request.form field.

import yaml
from flask import Flask, Response, request, render_template, g
from lti import LTI, LTIException
from controllers.index import Index
from controllers.answer import Answer
from controllers.question import QuestionController as Question
from controllers.tags import Modifytags, AssignTags
from controllers.ratings import AssignRatings
from controllers.review import ReviewAnswer
from controllers.stats import Stats

app = Flask(__name__)
app.debug = True
app.secret_key = "Hurdygurdy"  # Used for Flask sessions, TODO: config?


@app.before_request
def init_lti():
    """Starts (or resumes) the LTI session before anything else is handled.

    When no LTI session is available, an error page will be displayed."""

    params = {}
    if request.method == 'POST':
        params = request.form.to_dict()
    else:
        params = request.args.to_dict()

    try:
        g.lti = LTI(request.url, params, dict(request.headers))
    except LTIException as error:
        ret = "Error getting LTI data. Did you run this tool via a " + \
            "consumer such as Sakai?"
        if app.debug:
            ret += "<hr>Debug info:<br/>%s" % str(error)
        return ret


# define the routes for our application
@app.route("/", methods=['GET', 'POST'])
def home():
    ctrler = Index()
    return ctrler.render()


@app.route("/debug", methods=['GET', 'POST'])
def launch():
    ctrler = Index(debug=True)
    return ctrler.render()

@app.route("/stats", methods=['GET', 'POST'])
def show_stats():
  ctrler = Stats()
  return ctrler.render()
  


@app.route("/edit_question", methods=['GET', 'POST'])
def edit_question():
    return Question.edit_question(request.args['id'],
                                  request.args['text'],
                                  False)

# this route is called to toggle a question's availability


@app.route("/toggle_question", methods=['GET', 'POST'])
def toggle_question():
    return Question.toggle_question(request.args['id'])

# this route is used to ask a question to students


@app.route("/question", methods=['GET', 'POST'])
def ask_question():
    if g.lti.is_instructor() == False:
        return render_template("access_restricted.html")

    return Question.ask_question(g.lti.get_user_id())

# this route is used for the feedback from inserting the question into the
# database, it also inserts the question into the database


@app.route("/handle_question", methods=['POST'])
def handle_question():
    if g.lti.is_instructor() == False:
        return render_template("access_restricted.html")
    try:
        request.form['active']
        isActive = True
    except:
        isActive = False
    return Question.create_question(request.form['question'],
                                    g.lti.get_user_id(),
                                    g.lti.get_course_id(),
                                    isActive,
                                    request.form['time'])


@app.route("/question_list", methods=['GET', 'POST'])
def list_questions():
    return Question.get_list()


@app.route("/delete_question/<id>", methods=['GET', 'POST'])
def delete_question(id):
    return Question.delete_question(id)


@app.route("/question_export", methods=['GET', 'POST'])
def question_export():
    exp = Question.export_course(g.lti.get_course_id())
    exp = yaml.dump(exp, default_flow_style=False)
    return Response(exp,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment;filename=questions_%s.yaml" %
                    g.lti.get_course_name()})

@app.route("/question_import", methods=['GET', 'POST'])
def question_import():
    list = yaml.load(request.args['file'])
    print list

@app.route("/managetags", methods=['GET', 'POST'])
def managetags():
    ctrler = Modifytags()
    return ctrler.render()


@app.route("/addtag", methods=['POST'])
def addtags():
    ctrler = Modifytags()
    ctrler.addtag(request)
    return ctrler.render()


@app.route("/removetag", methods=['POST'])
def removetags():
    ctrler = Modifytags()
    ctrler.deletetag(request)
    return ctrler.render()


@app.route("/answer", methods=['GET', 'POST'])
def answerForm():
    ctrler = Answer(request)
    return ctrler.render()


@app.route("/assigntags", methods=['POST', 'GET'])
def assign_tags():
    ctrler = AssignTags(1)
    return ctrler.render()


@app.route("/assigntags_done", methods=['POST'])
def handle_assign_tags():
    ctrler = AssignTags.assign(request)
    return "<a href='/'>back to main</a>"
    
@app.route("/removetags_done",methods=['POST'])
def handle_assign_tags():
    ctrler = AssignTags.remove(request)
    return "<a href='/'>back to main</a>"

@app.route("/assignratings", methods=['POST', 'GET'])
def assign_ratings():
    ctrler = AssignRatings(1)
    return ctrler.render()


@app.route("/assignratings_done", methods=['POST'])
def handle_assign_ratings():
    ctrler = AssignRatings.assign(request)
    return "<a href='/'>back to main</a>"

"""
To review a answer, return reviewanswer.review(x) should be called from the
controller deciding wich answer to review, this url handles storing the reviews
in the database (given a user has permission to do so)
"""
@app.route("/reviewanswer",methods=['POST', 'GET'])
def handle_review_answer():
    ctrler = ReviewAnswer(request)
    return Index(request).render()

@app.route("/reviewanswer_stub", methods=["POST", "GET"])
def do_review_answer_stub():
    return ReviewAnswer.review(1)

@app.route("/filteranswers", methods=['POST', 'GET'])
def answerFilter():
    ctrler = Answer(request)
    return ctrler.render_filtered()


@app.route("/filteranswers/<questionid>", methods=['POST', 'GET'])
def answerFilterByQuestionID(questionid):
    ctrler = Answer(request)
    return ctrler.render_filtered_by_questionid(questionid)


@app.route("/has_new_question", methods=['GET', 'POST'])
def has_new_question():
    ctrler = Index()
    return ctrler.has_new_question()

@app.route("/logout")
def logout():
    g.lti.destroy()
    return "Logged out..."

if __name__ == '__main__':
    app.run()
