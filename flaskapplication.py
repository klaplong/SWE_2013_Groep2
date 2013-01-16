# Author : Dexter Drupsteen
# Descrp : Contains routing and calling of the controllers
# Changes:
# Comment:

import yaml
from flask import Flask, Response, request, render_template, g

from lti import LTI, LTIException
from controllers import index, answer, question

app = Flask(__name__)
app.debug = True
app.secret_key = "Hurdygurdy"

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
@app.route("/",methods=['GET', 'POST'])
def home():
    ctrler = index.Index(request)
    return ctrler.render()

@app.route("/test",methods=['POST'])
def test():
    return "You posted it didn't you?"

@app.route("/launch",methods=['POST'])
def launch():
    ctrler = index.Index(request)
    return ctrler.render()

@app.route("/question",methods=['POST'])
def ask_question():
    if g.lti.is_instructor() == False:
      return render_template("access_restricted.html")

    return question.questionController.ask_question(g.lti.get_user_id())

@app.route("/handleQuestion",methods=['POST'])
def handle_question():
    if g.lti.is_instructor() == False:
      return render_template("access_restricted.html")
    return question.questionController.create_question(request.form['question'],g.lti.get_user_id(),g.lti.get_course_id(),request.form['time'])


@app.route("/deleteQuestion/<id>", methods=['POST'])
def delete_question(id):
    return question.questionController.delete_question(id)

@app.route("/question_export", methods=['GET', 'POST'])
def question_export():
    exp = question.questionController.exportCourse(g.lti.get_course_id())
    print exp
    exp = yaml.dump(exp, default_flow_style=False)
    return Response(exp,
            mimetype="text/plain",
            headers={"Content-Disposition":
                "attachment;filename=questions_%s.txt" %
                    g.lti.get_course_name()})


@app.route("/answer",methods=['POST'])
def answerForm():
    ctrler = answer.Answer(request)
    return ctrler.render()

@app.route("/logout")
def logout():
    g.lti.destroy()
    return "Logged out..."

if __name__ == '__main__':
        app.run()

