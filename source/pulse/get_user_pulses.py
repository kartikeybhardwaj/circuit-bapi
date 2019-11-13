import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_user_pulses import validate_get_user_pulses_schema

from database.user.user import DBUser
from database.pulse.pulse import DBPulse

dbu = DBUser()
dbpu = DBPulse()

# fetch active pulses only in user's access projectId

class GetUserPulsesResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_user_pulses_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def getLimitedPulseIdsForUser(self, userId: str) -> list:
        return dbu.getAccessibleUserPulses(userId)

    def convertMongoDBObjectsToObjects(self, pulses: "list of dict") -> "list of dict":
        for pulse in pulses:
            pulse["_id"] = pulse["_id"]["$oid"]
            pulse["timeline"]["begin"] = pulse["timeline"]["begin"]["$date"]
            pulse["timeline"]["end"] = pulse["timeline"]["end"]["$date"]
            pulse["linkedProjectId"] = pulse["linkedProjectId"]["$oid"]
            pulse["linkedMilestoneId"] = pulse["linkedMilestoneId"]["$oid"]
        return pulses

    def on_get(self, req, resp):
        requestObj = req.params
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
        try:
            if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                # check if user is superuser
                responseObj["responseId"] = 109
                responseObj["message"] = "Unauthorized access"
            elif dbu.countDocumentsByUsername(requestObj["username"]) != 1:
                # check if user exist
                responseObj["responseId"] = 107
                responseObj["message"] = "User does not exist"
            else:
                # 01. get userId
                userId = dbu.getIdByUsername(requestObj["username"])
                # 02. get user accessible pulses
                pulseIds = self.getLimitedPulseIdsForUser(userId)
                # 03. get activePulses from pulseIds
                pulses = dbpu.getLesserPulsesByIds(pulseIds)
                # 04. clean up mongo objects
                pulses = self.convertMongoDBObjectsToObjects(pulses)
                # 05. attach pulses in response
                responseObj["data"]["pulses"] = pulses
                # 06. set responseId to success
                responseObj["responseId"] = 211
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            responseObj["message"] = str(ex)
        resp.media = responseObj
