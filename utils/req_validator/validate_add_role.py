validate_add_role_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\-\ ]*$",
            "minLength": 2,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "minLength": 4,
            "maxLength": 400
        },
        "canModifyUsersRole": {
            "type": "boolean"
        },
        "canModifyLocations": {
            "type": "boolean"
        },
        "canModifyProjects": {
            "type": "boolean"
        },
        "canModifyMilestones": {
            "type": "boolean"
        },
        "canModifyPulses": {
            "type": "boolean"
        }
    },
    "required": [
        "title",
        "description",
        "canModifyUsersRole",
        "canModifyLocations",
        "canModifyProjects",
        "canModifyMilestones",
        "canModifyPulses"
    ],
    "additionalProperties": False
}
