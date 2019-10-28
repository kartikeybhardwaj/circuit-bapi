from pymongo import MongoClient

class DBCreator:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def create(self) -> bool:
        success = False
        try:
            self.__db.create_collection("counter")
            self.__db.create_collection("locations")
            self.__db.create_collection("metaMilestones")
            self.__db.create_collection("metaProjects")
            self.__db.create_collection("metaPulse")
            self.__db.create_collection("milestones")
            self.__db.create_collection("projects")
            self.__db.create_collection("pulses")
            self.__db.create_collection("roles")
            self.__db.create_collection("users")
            counter = [{
                "for": "locations",
                "count": 0
            }, {
                "for": "metaMilestones",
                "count": 0
            }, {
                "for": "metaProjects",
                "count": 0
            }, {
                "for": "metaPulse",
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
                "count": 0
            }, {
                "for": "users",
                "count": 0
            }]
            self.__db.counter.insert_many(counter)
            success = True
        except Exception as ex:
            print(ex)
        return success
