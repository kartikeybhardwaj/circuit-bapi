import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_non_availability import validate_add_non_availability_schema

from database.user.user import DBUser
from utils.utils import Utils

dbu = DBUser()
utils = Utils()

class AddNonAvailabilityResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_non_availability_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        success = True
        message = ""
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        # end should be greater than begin
        if not tend > tbegin:
            success = False
            message = "Invalid timeline"
        return [success, message]

    """
    REQUEST:
        "reason": str
        "timeline": dict
            "begin": str
            "end": str
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
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "schema validation failed"))
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            log.info((thisFilename, inspect.currentframe().f_code.co_name, "schema validation successful"))
            # validate timeline
            afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
            if not afterValidationTimeline[0]:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid timeline"))
                responseObj["responseId"] = 110
                responseObj["message"] = afterValidationTimeline[1]
            else:
                # validation collision of dates
                overlappedReason = dbu.getCollisionNonAvailabilityReason(req.params["kartoon-fapi-incoming"]["_id"], requestObj["timeline"])
                if overlappedReason:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "timeline overlap"))
                    responseObj["responseId"] = 110
                    responseObj["data"]["reason"] = overlappedReason
                    responseObj["message"] = "There is overlap with another blockage"
                else:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                    try:
                        # insert non-availability
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                        dbu.insertNonAvailability(req.params["kartoon-fapi-incoming"]["_id"], requestObj["reason"], requestObj["timeline"])
                        responseObj["responseId"] = 211
                    except Exception as ex:
                        log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                        responseObj["message"] = str(ex)
        resp.media = responseObj
