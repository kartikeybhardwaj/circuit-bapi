from pymongo import MongoClient
from constants.dbpath import db_path

class DBDestroyer:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient(db_path)
        self.__db = self.__client.circuit

    def destroy(self) -> bool:
        success = False
        try:
            self.__db.drop_collection("counter")
            self.__db.drop_collection("locations")
            self.__db.drop_collection("metaMilestones")
            self.__db.drop_collection("metaProjects")
            self.__db.drop_collection("metaPulses")
            self.__db.drop_collection("milestones")
            self.__db.drop_collection("projects")
            self.__db.drop_collection("pulses")
            self.__db.drop_collection("roles")
            self.__db.drop_collection("users")
            success = True
        except Exception as ex:
            print(ex)
        return success
