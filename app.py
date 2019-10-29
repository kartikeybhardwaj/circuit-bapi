import falcon
from falcon_cors import CORS

from middleware.middleware import Middleware
from src.extras.status import StatusResource
from src.extras.creator import CreatorResource
from src.extras.destroyer import DestroyerResource
from src.user.add_superuser import AddSuperuserResource
from src.project.add_meta_project import AddMetaProjectResource
from src.milestone.add_meta_milestone import AddMetaMilestoneResource
from src.pulse.add_meta_pulse import AddMetaPulseResource
from src.project.add_project import AddProjectResource
from src.project.get_my_projects import GetMyProjectsResource

cors = CORS(allow_origins_list = ["http://localhost:4200"],
            allow_all_headers = True,
            allow_all_methods = True)

api = falcon.API(middleware = [
    cors.middleware,
    Middleware()
])

api.add_route("/", StatusResource())
api.add_route("/creator", CreatorResource())
api.add_route("/destroyer", DestroyerResource())
api.add_route("/add-superuser", AddSuperuserResource())
api.add_route("/add-meta-project", AddMetaProjectResource())
api.add_route("/add-meta-milestone", AddMetaMilestoneResource())
api.add_route("/add-meta-pulse", AddMetaPulseResource())
api.add_route("/add-project", AddProjectResource())
api.add_route("/get-my-projects", GetMyProjectsResource())
