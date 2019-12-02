validate_get_pulse_schema = {
    "type": "object",
    "properties": {
        "projectId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        }, "milestoneId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        }, "pulseId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        }
    },
    "required": [
        "projectId",
        "milestoneId",
        "pulseId"
    ]
}
