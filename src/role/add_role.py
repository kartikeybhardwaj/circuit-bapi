from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_role import validate_add_role_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.role.role import DBRole

class AddRoleResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_role_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    """
    REQUEST:
        "title": str
        "description": str
        "canModifyUsersRole": bool
        "canModifyLocations": bool
        "canModifyProjects": bool
        "canModifyMilestones": bool
        "canModifyPulses": bool
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
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # TODO: check if role title already exists
                    dbc = DBCounter()
                    index = dbc.getNewRoleIndex()
                    dbc.incrementRoleIndex()
                    dataToBeInserted = {}
                    dataToBeInserted["index"] = index
                    dataToBeInserted["isActive"] = True
                    dataToBeInserted["title"] = requestObj["title"]
                    dataToBeInserted["description"] = requestObj["description"]
                    dataToBeInserted["canModifyUsersRole"] = requestObj["canModifyUsersRole"]
                    dataToBeInserted["canModifyLocations"] = requestObj["canModifyLocations"]
                    dataToBeInserted["canModifyProjects"] = requestObj["canModifyProjects"]
                    dataToBeInserted["canModifyMilestones"] = requestObj["canModifyMilestones"]
                    dataToBeInserted["canModifyPulses"] = requestObj["canModifyPulses"]
                    dataToBeInserted["meta"] = {
                        "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                        "addedOn": datetime.datetime.utcnow(),
                        "lastUpdatedBy": None,
                        "lastUpdatedOn": None
                    }
                    dbr = DBRole()
                    responseObj["data"]["_id"] = dbr.insertRole(dataToBeInserted)
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
