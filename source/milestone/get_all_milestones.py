import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from database.user.user import DBUser
from database.milestone.milestone import DBMilestone

dbu = DBUser()
dbm = DBMilestone()

# verify access for user
### is user superuser

class GetAllMilestonesResource:

    def convertMongoDBObjectsToObjects(self, milestones: "list of dict") -> "list of dict":
        for milestone in milestones:
            milestone["_id"] = milestone["_id"]["$oid"]
            milestone["timeline"]["begin"] = milestone["timeline"]["begin"]["$date"]
            milestone["timeline"]["end"] = milestone["timeline"]["end"]["$date"]
            milestone["linkedProjectId"] = milestone["linkedProjectId"]["$oid"]
        return milestones

    def on_get(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
            responseObj["responseId"] = 109
            responseObj["message"] = "Unauthorized access"
        else:
            try:
                # 01. get all active milestones
                milestones = dbm.getAllMilestones()
                # 02. clean up mongo objects
                milestones = self.convertMongoDBObjectsToObjects(milestones)
                # 03. attach milestones in response
                responseObj["data"]["milestones"] = milestones
                # 04. set responseId to success
                responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
