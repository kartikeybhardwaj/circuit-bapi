from pymongo import MongoClient
from constants.dbpath import db_path

class DBCreator:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient(db_path)
        self.__db = self.__client.circuit

    def create(self) -> bool:
        success = False
        try:
            self.__db.create_collection("counter")
            self.__db.create_collection("locations")
            self.__db.create_collection("metaMilestones")
            self.__db.create_collection("metaProjects")
            self.__db.create_collection("metaPulses")
            self.__db.create_collection("milestones")
            self.__db.create_collection("projects")
            self.__db.create_collection("pulses")
            self.__db.create_collection("roles")
            self.__db.create_collection("users")
            counter = [{
                "for": "locations",
                "count": 2
            }, {
                "for": "metaMilestones",
                "count": 0
            }, {
                "for": "metaProjects",
                "count": 0
            }, {
                "for": "metaPulses",
                "count": 0
            },{
                "for": "milestones",
                "count": 0
            }, {
                "for": "projects",
                "count": 0
            }, {
                "for": "pulses",
                "count": 0
            }, {
                "for": "roles",
                "count": 3
            }, {
                "for": "users",
                "count": 0
            }]
            self.__db.counter.insert_many(counter)
            roles = [{
                "index": 1,
                "isActive": True,
                "title": "Owner",
                "description": "",
                "canModifyUsersRole": True,
                "canModifyLocations": True,
                "canModifyProjects": True,
                "canModifyMilestones": True,
                "canModifyPulses": True,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }, {
                "index": 2,
                "isActive": True,
                "title": "Project Manager",
                "description": "",
                "canModifyUsersRole": True,
                "canModifyLocations": True,
                "canModifyProjects": True,
                "canModifyMilestones": True,
                "canModifyPulses": True,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }, {
                "index": 3,
                "isActive": True,
                "title": "Project Member",
                "description": "",
                "canModifyUsersRole": False,
                "canModifyLocations": True,
                "canModifyProjects": False,
                "canModifyMilestones": True,
                "canModifyPulses": True,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }, {
                "index": 4,
                "isActive": True,
                "title": "Guest",
                "description": "",
                "canModifyUsersRole": False,
                "canModifyLocations": False,
                "canModifyProjects": False,
                "canModifyMilestones": False,
                "canModifyPulses": False,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }]
            self.__db.roles.insert_many(roles)
            locations = [{
                "index": 1,
                "city": "Mysuru",
                "country": "India",
                "isActive": True,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }, {
                "index": 2,
                "city": "Bengaluru",
                "country": "India",
                "isActive": True,
                "meta": {
                    "addedBy": None,
                    "addedOn": None,
                    "lastUpdatedBy": None,
                    "lastUpdatedOn": None
                }
            }]
            self.__db.locations.insert_many(locations)
            success = True
        except Exception as ex:
            print(ex)
        return success
