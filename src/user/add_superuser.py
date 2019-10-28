from database.user.user import DBUser
from database.counter.counter import DBCounter

class AddSuperuserResource:

    def validateUser(self, username: str) -> bool:
        success = False
        # TODO: check if this user really exists using LDAP
        if (username and len(username) > 3):
            success = True
        return success

    """
    REQUEST:
        "username": "<USERNAME>"
    """
    def on_post(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            requestObj = req.media
            # validate incoming username
            if self.validateUser(requestObj.get("username", "")):
                # TODO: get display name of this user
                dbu = DBUser()
                # check if user exists
                userExists = dbu.countDocuments(requestObj["username"])
                if userExists:
                    # if user exists
                    dbu.updateUserToSuperuser()
                else:
                    # if user doesn't exist
                    dbc = DBCounter()
                    index = dbc.getNewUserIndex()
                    dbc.incrementUserIndex()
                    dbu.insertSuperuser(
                        index,
                        requestObj["username"],
                        # TODO: display name of this user will come here
                        req.params["kartoon-fapi-incoming"]["displayname"]
                    )
                responseObj["responseId"] = 211
            else:
                responseObj["responseId"] = 110
                responseObj["message"] = ""
        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
