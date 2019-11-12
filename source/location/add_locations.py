import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_locations import validate_add_locations_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.location.location import DBLocation

dbu = DBUser()
dbc = DBCounter()
dbl = DBLocation()

class AddLocationsResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_locations_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    """
    REQUEST:
        "names": list of str
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
            try:
                # check if user is superuser
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "user is not superuser"))
                    # if not
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "user is superuser"))
                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to insert"))
                    # if yes
                    dataToBeInserted = []
                    # extraData to be appended with every location
                    extraData = {
                        "isActive": True,
                        "meta": {
                            "addedBy": ObjectId(req.params["kartoon-fapi-incoming"]["_id"]),
                            "addedOn": datetime.datetime.utcnow(),
                            "lastUpdatedBy": None,
                            "lastUpdatedOn": None
                        }
                    }
                    insertedIds = []
                    alreadyExists = []
                    for i in range(len(requestObj["names"])):
                        # 01. check if this location already exist
                        existingLocId = dbl.getLocationIdByName(requestObj["names"][i])
                        if not existingLocId:
                            # if not
                            dataToBeInserted.append({})
                            # 01. 01. get index for new location
                            index = dbc.getNewLocationIndex()
                            # 01. 02. increment location counter
                            dbc.incrementLocationIndex()
                            # 01. 03. prepare dataToBeInserted
                            dataToBeInserted[i]["index"] = index
                            dataToBeInserted[i]["name"] = requestObj["names"][i]
                            dataToBeInserted[i].update(extraData)
                        else:
                            # if yes
                            alreadyExists.append({
                                "_id": existingLocId,
                                "name": requestObj["names"][i]
                            })
                    if len(dataToBeInserted) > 0:
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                        # 02. insert dataToBeInserted in locations
                        insertedIds = dbl.insertLocations(dataToBeInserted)
                    else: log.warn((thisFilename, inspect.currentframe().f_code.co_name, "there is no data to insert"))
                    # 03. attach insertedIds in response
                    responseObj["data"]["_ids"] = insertedIds
                    # 04. attach alreadyExists in response
                    responseObj["data"]["alreadyExists"] = alreadyExists
                    # 05. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
