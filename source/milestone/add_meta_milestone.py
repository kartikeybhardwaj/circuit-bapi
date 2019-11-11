from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_meta_milestone import validate_add_meta_milestone_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.milestone.milestone import DBMilestone

dbu = DBUser()
dbc = DBCounter()
dbm = DBMilestone()

class AddMetaMilestoneResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_meta_milestone_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["fields"] = requestObj["fields"]
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(userId),
            "addedOn": datetime.datetime.utcnow(),
            "lastUpdatedBy": None,
            "lastUpdatedOn": None
        }
        return dataToBeInserted

    """
    REQUEST:
        "title": str
        "description": str
        "fields": dict
    """
    def on_post(self, req, resp):
        requestObj = req.media
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        # validate schema
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            try:
                # check if user is superuser
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    # if not
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # if yes
                    # 01. get index for new metaMilestone
                    index = dbc.getNewMetaMilestoneIndex()
                    # 02. increment metaMilestone counter
                    dbc.incrementMetaMilestoneIndex()
                    # 03. prepare dataToBeInserted
                    dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                    # 04. insert dataToBeInserted in metaMilestone and attach metaMilestoneId in response
                    responseObj["data"]["_id"] = dbm.insertMetaMilestone(dataToBeInserted)
                    # 05. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
