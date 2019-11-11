from database.user.user import DBUser
from source.user.add_user import AddUserResource

dbu = DBUser()
aur = AddUserResource()

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
            # 01. get user by username
            user = dbu.getUserByUsername(req.params["kartoon-fapi-incoming"]["username"])
            # 02. if user does not exist
            if not user:
                # 02. 01. add user
                aur.addUser(
                    req.params["kartoon-fapi-incoming"]["username"],
                    req.params["kartoon-fapi-incoming"]["displayname"],
                    None
                )
                # 02. 02. get added user by username
                user = dbu.getUserByUsername(req.params["kartoon-fapi-incoming"]["username"])
            # 03. update users' last seen
            dbu.updateLastSeen(user["_id"]["$oid"])
            # 04. attach user document in response
            responseObj["data"] = user
            # 05. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
