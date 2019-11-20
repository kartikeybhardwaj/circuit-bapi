import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_get_overlaps_creating_pulse import validate_get_overlaps_creating_pulse_schema

from database.user.user import DBUser
from database.milestone.milestone import DBMilestone
from utils.utils import Utils

dbu = DBUser()
dbm = DBMilestone()
utils = Utils()

class GetOverlapsCreatingPulseResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_get_overlaps_creating_pulse_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def validateMilestoneId(self, milestoneId: str) -> [bool, str]:
        success = False
        message = ""
        try:
            ObjectId(milestoneId)
            success = True
        except Exception as ex:
            message = "Invalid milestoneId"
        return [success, message]

    def validateMemberIds(self, memberIds: list) -> [bool, str]:
        success = False
        message = ""
        validation = {
            "validIds": [],
            "invalidIds": []
        }
        for memberId in memberIds:
            try:
                ObjectId(memberId)
                validation["validIds"].append(memberId)
            except Exception as ex:
                validation["invalidIds"].append(memberId)
        if len(validation["invalidIds"]) == 0:
            success = True
        return [success, validation]

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
        "milestoneId": str
        "timeline": dict
            "begin": str
            "end": str
        "members": array of str
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
            # validate timeline
            afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
            if not afterValidationTimeline[0]:
                responseObj["responseId"] = 110
                responseObj["message"] = afterValidationTimeline[1]
            else:
                # validate milestoneId
                afterValidationMilestoneId = self.validateMilestoneId(requestObj["milestoneId"])
                if not afterValidationMilestoneId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationMilestoneId[1]
                else:
                    # validate members
                    afterValidationMemberIds = self.validateMemberIds(requestObj["members"])
                    if not afterValidationMemberIds[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = "Invalid memberIds"
                        responseObj["data"] = afterValidationMemberIds[1]
                    else:
                        try:
                            requestObj["timeline"]["begin"] = utils.getDateFromUTCString(requestObj["timeline"]["begin"])
                            requestObj["timeline"]["end"] = utils.getDateFromUTCString(requestObj["timeline"]["end"])
                            # for every member, check their availability
                            for memberId in requestObj["members"]:
                                responseObj["data"][memberId] = {}
                                # check if this memberId overlaps with nonAvailability
                                cna = dbu.getCollisionNonAvailability(memberId, requestObj["timeline"])
                                if cna:
                                    responseObj["data"][memberId]["status"] = False
                                    responseObj["data"][memberId]["nonAvailability"] = cna["nonAvailability"][0]
                                    responseObj["data"][memberId]["nonAvailability"]["timeline"]["begin"] = responseObj["data"][memberId]["nonAvailability"]["timeline"]["begin"]["$date"]
                                    responseObj["data"][memberId]["nonAvailability"]["timeline"]["end"] = responseObj["data"][memberId]["nonAvailability"]["timeline"]["end"]["$date"]
                                    responseObj["data"][memberId]["otherLocations"] = None
                                    responseObj["data"][memberId]["baseLocationMatch"] = None
                                else:
                                    # check if this memberId overlaps with travelLocation
                                    ctl = dbu.getCollisionTravelLocation(memberId, requestObj["timeline"])
                                    if ctl:
                                        responseObj["data"][memberId]["status"] = False
                                        responseObj["data"][memberId]["nonAvailability"] = None
                                        responseObj["data"][memberId]["otherLocations"] = ctl["otherLocations"][0]
                                        responseObj["data"][memberId]["otherLocations"]["locationId"] = responseObj["data"][memberId]["otherLocations"]["locationId"]["$oid"]
                                        responseObj["data"][memberId]["otherLocations"]["timeline"]["begin"] = responseObj["data"][memberId]["otherLocations"]["timeline"]["begin"]["$date"]
                                        responseObj["data"][memberId]["otherLocations"]["timeline"]["end"] = responseObj["data"][memberId]["otherLocations"]["timeline"]["end"]["$date"]
                                        responseObj["data"][memberId]["baseLocationMatch"] = None
                                    else:
                                        # get locationId of member
                                        memberLocationId = dbu.getBaseLocationByUserId(memberId)
                                        # get locationId of mileststone
                                        milestoneLocationId = dbm.getLocationId(requestObj["milestoneId"])
                                        # check if memberLocationId is equal to milestoneLocationId
                                        if memberLocationId != milestoneLocationId:
                                            responseObj["data"][memberId]["status"] = False
                                            responseObj["data"][memberId]["nonAvailability"] = None
                                            responseObj["data"][memberId]["otherLocations"] = None
                                            responseObj["data"][memberId]["baseLocationMatch"] = memberLocationId
                                        else:
                                            responseObj["data"][memberId]["status"] = True
                                            responseObj["data"][memberId]["nonAvailability"] = None
                                            responseObj["data"][memberId]["otherLocations"] = None
                                            responseObj["data"][memberId]["baseLocationMatch"] = memberLocationId
                            responseObj["responseId"] = 211
                        except Exception as ex:
                            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                            responseObj["message"] = str(ex)
        resp.media = responseObj
