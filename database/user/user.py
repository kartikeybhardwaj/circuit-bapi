from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

from utils.utils import Utils
utils = Utils()

class DBUser:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocumentsById(self, userId: str) -> int:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isActive": True
        })

    def countDocumentsByUsername(self, username: str) -> int:
        return self.__db.users.count_documents({
            "username": username,
            "isActive": True
        })

    def getUserByUsername(self, username: str) -> dict:
        result = self.__db.users.find_one({
            "username": username,
            "isActive": True
        })
        return json.loads(dumps(result))

    def getIdByUsername(self, username: str) -> str:
        _id = self.__db.users.find_one({
            "username": username,
            "isActive": True
        }, {
            "_id": 1
        })
        return str(_id["_id"]) if _id else None

    def checkIfUserIsSuperuser(self, userId: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isActive": True,
            "isSuperuser": True
        }) == 1

    def getAccessibleProjects(self, userId: str) -> list:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True
        }, {
            "_id": 0,
            "access.projects.projectId": 1
        })
        return json.loads(dumps(result))["access"]["projects"]

    def getAccessibleMilestonesInProject(self, userId: str, projectId: str) -> list:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId)
        }, {
            "_id": 0,
            "access.projects.milestones.milestoneId": 1
        })
        return json.loads(dumps(result))["access"]["projects"][0]["milestones"]

    def getAccessiblePulsesInMilestone(self, userId: str, projectId: str, milestoneId: str) -> list:
        return self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.milestones.milestoneId": ObjectId(milestoneId)
        }, {
            "_id": 0,
            "access.projects.milestones.$.pulses": 1
        })["access"]["projects"]["milestones"]["pulses"]

    def getAccessibleUserPulses(self, userId: str) -> list:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True
        }, {
            "_id": 0,
            "access.projects.milestones.pulses": 1
        })["access"]
        result = json.loads(dumps(result))
        _out = []
        for project in result["projects"]:
            for milestone in project["milestones"]:
                for pulse in milestone["pulses"]:
                    _out.append(pulse["$oid"])
        return _out

    def getAccessibleUserPulsesInProjectId(self, userId: str, projectId: str) -> list:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId)
        }, {
            "_id": 0,
            "access.projects.$.milestones.pulses": 1
        })["access"]["projects"][0]["milestones"]
        result = json.loads(dumps(result))
        _out = []
        for milestone in result:
            if "pulses" in milestone:
                for pulse in milestone["pulses"]:
                    _out.append(pulse["$oid"])
        return _out

    def getActiveUserIdsByIds(self, userIds: "list of str") -> "list of dict":
        userIds = list(map(ObjectId, userIds))
        result = self.__db.users.find({
            "_id": {
                "$in": userIds
            },
            "isActive": True
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getUsernamesMapByIds(self, userIds: "list of str") -> "list of dict":
        userIds = list(map(ObjectId, userIds))
        result = self.__db.users.find({
            "_id": {
                "$in": userIds
            }
        }, {
            "_id": 1,
            "username": 1
        })
        return json.loads(dumps(result))

    def getBaseLocationByUserId(self, userId: str) -> str:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId)
        }, {
            "_id": 0,
            "baseLocation": 1
        })
        return result["baseLocation"]["$oid"] if result["baseLocation"] else None

    def updateUserToSuperuser(self, username: str) -> bool:
        return self.__db.users.update_one({
            "username": username,
            "isActive": True
        }, {
            "$set": {
                "isSuperuser": True
            }
        }).modified_count == 1

    def updateSuperuserToUser(self, username: str) -> bool:
        return self.__db.users.update_one({
            "username": username,
            "isActive": True
        }, {
            "$set": {
                "isSuperuser": False
            }
        }).modified_count == 1

    def updateLastSeen(self, userId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId),
            "isActive": True
        }, {
            "$set": {
                "meta.lastSeen": datetime.datetime.utcnow()
            }
        }).modified_count == 1

    def insertUser(self, user: dict) -> str:
        _id = self.__db.users.insert_one(user).inserted_id
        return str(_id)

    def insertAccessProjectId(self, userId: str, projectId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "access.projects": {
                    "projectId": ObjectId(projectId),
                    "milestones": []
                }
            }
        }).modified_count == 1

    def hasProjectAccess(self, userId: str, projectId: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId)
        }) == 1

    def hasMilestoneAccess(self, userId: str, projectId: str, milestoneId: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId),
            "access.projects.milestones.milestoneId": ObjectId(milestoneId)
        }) == 1

    def hasPulseAccess(self, userId: str, projectId: str, milestoneId: str, pulseId: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId),
            "access.projects.milestones.milestoneId": ObjectId(milestoneId),
            "access.projects.milestones.pulses": ObjectId(pulseId)
        }) == 1

    def insertAccessToMilestone(self, userId: str, projectId: str, milestoneId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId),
            "access.projects.projectId": ObjectId(projectId)
        }, {
            "$push": {
                "access.projects.$.milestones": {
                    "milestoneId": ObjectId(milestoneId),
                    "pulses": []
                }
            }
        }).modified_count == 1

    def insertAccessToPulse(self, userId: str, projectId: str, milestoneId: str, pulseId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "access.projects.$[i].milestones.$[j].pulses": ObjectId(pulseId)
            }
        }, array_filters = [{
                "i.projectId": ObjectId(projectId)
            }, {
                "j.milestoneId": ObjectId(milestoneId)
        }]).modified_count == 1

    def updateLocationId(self, userId: str, locationId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$set": {
                "baseLocation": ObjectId(locationId)
            }
        }).modified_count == 1

    def insertTravel(self, userId: str, locationId: str, timeline: dict) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "otherLocations": {
                    "locationId": ObjectId(locationId),
                    "timeline": {
                        "begin": timeline["begin"],
                        "end": timeline["end"]
                    }
                }
            }
        }).modified_count == 1

    def insertNonAvailability(self, userId: str, reason: str, timeline: dict) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "nonAvailability": {
                    "reason": reason,
                    "timeline": {
                        "begin": timeline["begin"],
                        "end": timeline["end"]
                    }
                }
            }
        }).modified_count == 1

    def getCollisionTravelLocationId(self, userId: str, timeline: dict) -> str:
        timeline["begin"] = utils.getDateFromUTCString(timeline["begin"])
        timeline["end"] = utils.getDateFromUTCString(timeline["end"])
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "otherLocations.timeline.begin": {
                "$lt": timeline["end"]
            },
            "otherLocations.timeline.end": {
                "$gt": timeline["begin"]
            }
        }, {
            "_id": 0,
            "otherLocations.locationId": 1
        })
        result = json.loads(dumps(result))
        return result["otherLocations"][0]["locationId"]["$oid"] if result else None

    def getCollisionNonAvailabilityReason(self, userId: str, timeline: dict) -> str:
        timeline["begin"] = utils.getDateFromUTCString(timeline["begin"])
        timeline["end"] = utils.getDateFromUTCString(timeline["end"])
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "nonAvailability.timeline.begin": {
                "$lt": timeline["end"]
            },
            "nonAvailability.timeline.end": {
                "$gt": timeline["begin"]
            }
        }, {
            "_id": 0,
            "nonAvailability.reason": 1
        })
        result = json.loads(dumps(result))
        return result["nonAvailability"][0]["reason"] if result else None

    def getCollisionTravelLocation(self, userId: str, timeline: dict) -> str:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "otherLocations.timeline.begin": {
                "$lt": timeline["end"]
            },
            "otherLocations.timeline.end": {
                "$gt": timeline["begin"]
            }
        }, {
            "_id": 0,
            "otherLocations": 1
        })
        return json.loads(dumps(result))

    def getCollisionNonAvailability(self, userId: str, timeline: dict) -> str:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId),
            "nonAvailability.timeline.begin": {
                "$lt": timeline["end"]
            },
            "nonAvailability.timeline.end": {
                "$gt": timeline["begin"]
            }
        }, {
            "_id": 0,
            "nonAvailability": 1
        })
        return json.loads(dumps(result))

    def matchesBaseLocation(self, userId: str, locationId: str) -> bool:
        result = self.__db.find_one({
            "_id": ObjectId(userId),
            "baseLocation": ObjectId(locationId)
        }, {
            "_id": 1
        })
        return True if result else False

    def getAccessPulseLength(self, userId: str, projectId: str, milestoneId: str) -> int:
        return len(self.__db.users.find_one({
            "_id": ObjectId(userId),
            "isActive": True,
            "access.projects.projectId": ObjectId(projectId),
            "access.projects.milestones.milestoneId": ObjectId(milestoneId)
        }, {
            "_id": 0,
            "access.projects.milestones.$.pulses": 1
        })["access"]["projects"][0]["milestones"][0]["pulses"])

    def removeAccessFromPulse(self, userId: str, projectId: str, milestoneId: str, pulseId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId),
        }, {
            "$pull": {
                "access.projects.$[i].milestones.$[j].pulses": ObjectId(pulseId)
            }
        }, array_filters = [{
                "i.projectId": ObjectId(projectId)
            }, {
                "j.milestoneId": ObjectId(milestoneId)
        }]).modified_count == 1

    def removeAccessFromMilestone(self, userId: str, projectId: str, milestoneId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$pull": {
                "access.projects.$[i].milestones": {
                    "milestoneId": ObjectId(milestoneId)
                }
            }
        }, array_filters = [{
                "i.projectId": ObjectId(projectId)
            }
        ]).modified_count == 1

    def removeAccessFromProject(self, userId: str, projectId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$pull": {
                "access.projects": {
                    "projectId": ObjectId(projectId)
                }
            }
        }).modified_count == 1
