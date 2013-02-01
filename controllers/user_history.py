from models.user_history import UserHistoryModel
from models.user import UserModel
from utilities import render_template

class UserHistory():
    def __init__(self, request):
        self.request = request
        
    def __repr__(self):
        return "<UserHistory ('%s', '%s', '%s', '%s')>" % (self.key, self.userid, self.time, self.trust)

    def render_by_userid(self, uid):
        return render_template('trustdata.html', data=UserHistoryModel.get_by_user_id_more(uid), data2=UserModel.by_user_id(uid))
        
    def render_adjust_trust(self, uid, trust):
        UserModel.setTrust(uid, trust)
        return render_template('trustdata_start.html', data=UserModel.get_all())
        