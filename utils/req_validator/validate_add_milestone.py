validate_add_milestone_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\-\ ]*$",
            "minLength": 4,
            "maxLength": 20
        },
        "description": {
            "type": "string",
            "minLength": 4,
            "maxLength": 40
        },
        "timeline": {
            "type": "object",
            "properties": {
                "begin": {
                    "type": "string",
                    "pattern": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z"
                },
                "end": {
                    "type": "string",
                    "pattern": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z"
                }
            },
            "required": [
                "begin",
                "end"
            ],
            "additionalProperties": False
        },
        "milestoneMetaId": {
            "type": [
                "string",
                "null"
            ],
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        },
        "fields": {
            "type": "array",
            "minItems": 0,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "minLength": 1
                    },
                    "value": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [
                    "key",
                    "value"
                ],
                "additionalProperties": False
            }
        },
        "linkedProjectId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        }
    },
    "required": [
        "title",
        "description",
        "milestoneMetaId",
        "fields",
        "linkedProjectId"
    ],
    "additionalProperties": False
}
