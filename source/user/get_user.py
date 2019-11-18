import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from database.user.user import DBUser
from source.user.add_user import AddUserResource

dbu = DBUser()
aur = AddUserResource()

class GetUserResource:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convertMongoDBObjectsToObjects(self, user: "list of dict") -> "list of dict":
        user["_id"] = user["_id"]["$oid"]
        if user["baseLocation"]:
            user["baseLocation"] = user["baseLocation"]["$oid"]
        for otherLocation in user["otherLocations"]:
            otherLocation["locationId"] = otherLocation["locationId"]["$oid"]
            otherLocation["timeline"]["begin"] = otherLocation["timeline"]["begin"]["$date"]
            otherLocation["timeline"]["end"] = otherLocation["timeline"]["end"]["$date"]
        for nonAvailability in user["nonAvailability"]:
            nonAvailability["timeline"]["begin"] = nonAvailability["timeline"]["begin"]["$date"]
            nonAvailability["timeline"]["end"] = nonAvailability["timeline"]["end"]["$date"]
        for project in user["access"]["projects"]:
            project["projectId"] = project["projectId"]["$oid"]
            for milestone in project["milestones"]:
                milestone["milestoneId"] = milestone["milestoneId"]["$oid"]
                milestone["pulses"] = [pulse["$oid"] for pulse in milestone["pulses"]]
        if user["meta"]["addedBy"]:
            user["meta"]["addedBy"] = user["meta"]["addedBy"]["$oid"]
        if user["meta"]["addedOn"]:
            user["meta"]["addedOn"] = user["meta"]["addedOn"]["$date"]
        if user["meta"]["lastSeen"]:
            user["meta"]["lastSeen"] = user["meta"]["lastSeen"]["$date"]
        return user

    """
    REQUEST:
        "username": str
        "displayname": str
    """
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
            # 04. clean up mongo objects
            user = self.convertMongoDBObjectsToObjects(user)
            # 05. attach user document in response
            responseObj["data"] = user
            # 06. set responseId to success
            responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
