from database.user.user import DBUser
from source.user.add_user import AddUserResource

class GetUserResource:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            dbu = DBUser()
            user = dbu.getUserByUsername(req.params["kartoon-fapi-incoming"]["username"])
            if not user:
                aur = AddUserResource()
                aur.addUser(
                    req.params["kartoon-fapi-incoming"]["username"],
                    req.params["kartoon-fapi-incoming"]["displayname"],
                    None
                )
                user = dbu.getUserByUsername(req.params["kartoon-fapi-incoming"]["username"])
            dbu.updateLastSeen(user["_id"]["$oid"])
            responseObj["data"] = user
            responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
