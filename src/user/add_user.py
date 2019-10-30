from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_user import validate_add_user_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter

class AddUserResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_user_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    """
    REQUEST:
        "username": str
        "displayname": str
    """
    def on_post(self, req, resp):
        requestObj = req.media
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            try:
                dbu = DBUser()
                userCount = dbu.countDocuments(requestObj["username"])
                if userCount == 1:
                    # if user exists
                    responseObj["responseId"] = 108
                    responseObj["message"] = "Already exists"
                elif userCount == 0:
                    # if user doesn't exist
                    dbc = DBCounter()
                    index = dbc.getNewUserIndex()
                    dbc.incrementUserIndex()
                    dataToBeInserted = {}
                    dataToBeInserted["index"] = index
                    dataToBeInserted["username"] = requestObj["username"]
                    dataToBeInserted["displayname"] = requestObj["displayname"]
                    dataToBeInserted["isSuperuser"] = False
                    dataToBeInserted["baseLocation"] = None
                    dataToBeInserted["otherLocations"] = []
                    dataToBeInserted["nonAvailability"] = []
                    dataToBeInserted["access"] = {
                        "projects": []
                    }
                    dataToBeInserted["meta"] = {
                        "addedBy": None,
                        "addedOn": datetime.datetime.utcnow(),
                        "lastSeen": None
                    }
                    responseObj["data"]["_id"] = dbu.insertUser(dataToBeInserted)
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = ex.message
        resp.media = responseObj