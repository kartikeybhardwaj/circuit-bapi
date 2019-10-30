from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_meta_pulse import validate_add_meta_pulse_schema_1, validate_add_meta_pulse_schema_2

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.pulse.pulse import DBPulse

class AddMetaPulseResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_meta_pulse_schema_1)
            success = True
        except Exception as ex1:
            message = ex1.message
            try:
                validate(instance=requestObj, schema=validate_add_meta_pulse_schema_2)
                success = True
            except Exception as ex2:
                message = ex2.message
        return [success, message]

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
                    index = dbc.getNewMetaPulseIndex()
                    dbc.incrementMetaPulseIndex()
                    dataToBeInserted = {}
                    dataToBeInserted["index"] = index
                    dataToBeInserted["isActive"] = True
                    dataToBeInserted["title"] = requestObj["title"]
                    dataToBeInserted["description"] = requestObj["description"]
                    dataToBeInserted["fields"] = requestObj["fields"]
                    dataToBeInserted["meta"] = {
                        "addedBy": req.params["kartoon-fapi-incoming"]["_id"],
                        "addedOn": datetime.datetime.utcnow(),
                        "lastUpdatedBy": None,
                        "lastUpdatedOn": None
                    }
                    dbpu = DBPulse()
                    responseObj["data"]["_id"] = dbpu.insertMetaPulse(dataToBeInserted)
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = ex.message
        resp.media = responseObj
