validate_get_project_schema = {
    "type": "object",
    "properties": {
        "projectId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        }
    },
    "required": [
        "projectId"
    ]
}
