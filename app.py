import falcon
from falcon_cors import CORS

from utils.log import logger as log

from middleware.middleware import Middleware
from source.extras.status import StatusResource
from source.extras.creator import CreatorResource
from source.extras.destroyer import DestroyerResource
from source.user.add_superuser import AddSuperuserResource
from source.project.add_meta_project import AddMetaProjectResource
from source.milestone.add_meta_milestone import AddMetaMilestoneResource
from source.pulse.add_meta_pulse import AddMetaPulseResource
from source.role.add_role import AddRoleResource
from source.location.add_locations import AddLocationsResource
from source.project.add_project import AddProjectResource
from source.milestone.add_milestone import AddMilestoneResource
from source.pulse.add_pulse import AddPulseResource
from source.user.get_user import GetUserResource
from source.role.get_roles import GetRolesResource
from source.project.get_projects import GetProjectsResource
from source.milestone.get_milestones import GetMilestonesResource
from source.pulse.get_pulses import GetPulsesResource
from source.project.get_meta_projects import GetMetaProjectsResource
from source.milestone.get_meta_milestones import GetMetaMilestonesResource
from source.pulse.get_meta_pulses import GetMetaPulsesResource
from source.pulse.get_my_pulses import GetMyPulsesResource
from source.pulse.update_pulse_timeline import UpdatePulseTimelineResource
from source.location.get_locations import GetLocationsResource
from source.location.update_base_location import UpdateBaseLocationResource
from source.user.add_travel import AddTravelResource
from source.user.add_non_availability import AddNonAvailabilityResource
from source.milestone.get_all_milestones import GetAllMilestonesResource
from source.pulse.get_user_pulses import GetUserPulsesResource
from source.user.get_overlaps_creating_pulse import GetOverlapsCreatingPulseResource
from source.project.get_project import GetProjectResource
from source.milestone.get_milestone import GetMilestoneResource
from source.pulse.get_pulse import GetPulseResource
from source.project.update_project import UpdateProjectResource
from source.milestone.update_milestone import UpdateMilestoneResource
from source.pulse.update_pulse import UpdatePulseResource

cors = CORS(allow_origins_list=["http://localhost:3100"],
            allow_credentials_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True)

api = falcon.API(middleware=[
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
api.add_route("/add-role", AddRoleResource())
api.add_route("/add-locations", AddLocationsResource())
api.add_route("/add-project", AddProjectResource())
api.add_route("/add-milestone", AddMilestoneResource())
api.add_route("/add-pulse", AddPulseResource())
api.add_route("/get-user", GetUserResource())
api.add_route("/get-roles", GetRolesResource())
api.add_route("/get-project", GetProjectResource())
api.add_route("/get-projects", GetProjectsResource())
api.add_route("/get-milestone", GetMilestoneResource())
api.add_route("/get-milestones", GetMilestonesResource())
api.add_route("/get-pulse", GetPulseResource())
api.add_route("/get-pulses", GetPulsesResource())
api.add_route("/get-meta-projects", GetMetaProjectsResource())
api.add_route("/get-meta-milestones", GetMetaMilestonesResource())
api.add_route("/get-meta-pulses", GetMetaPulsesResource())
api.add_route("/get-my-pulses", GetMyPulsesResource())
api.add_route("/update-pulse-timeline", UpdatePulseTimelineResource())
api.add_route("/get-locations", GetLocationsResource())
api.add_route("/update-base-location", UpdateBaseLocationResource())
api.add_route("/add-travel", AddTravelResource())
api.add_route("/add-non-availability", AddNonAvailabilityResource())
api.add_route("/get-all-milestones", GetAllMilestonesResource())
api.add_route("/get-user-pulses", GetUserPulsesResource())
api.add_route("/get-overlaps-creating-pulse", GetOverlapsCreatingPulseResource())
api.add_route("/update-project", UpdateProjectResource())
api.add_route("/update-milestone", UpdateMilestoneResource())
api.add_route("/update-pulse", UpdatePulseResource())

log.info("Circuit is up and running..")
