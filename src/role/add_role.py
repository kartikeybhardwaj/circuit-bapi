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
                    dbc = DBCounter()
                    index = dbc.getNewRoleIndex()
                    dbc.incrementRoleIndex()
                    requestObj["index"] = index
                    requestObj["isActive"] = True
                    requestObj["meta"] = {
                        "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                        "addedOn": datetime.datetime.utcnow(),
                        "lastUpdatedBy": None,
                        "lastUpdatedOn": None
                    }
                    dbr = DBRole()
                    responseObj["data"]["_id"] = dbr.insertRole(requestObj)
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = ex.message
        resp.media = responseObj
