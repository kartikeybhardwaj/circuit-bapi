validate_add_project_schema = {
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
        "visibility": {
            "type": "string",
            "enum": [
                "public",
                "internal",
                "private"
            ]
        },
        "members": {
            "type": "array",
            "minItems": 0,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\.\_]*$",
                        "minLength": 4
                    },
                    "displayname": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\.\_\ ]*$",
                        "minLength": 4
                    },
                    "roleId": {
                        "type": "string",
                        "pattern": "^[0-9a-z]*$",
                        "minLength": 24,
                        "maxLength": 24
                    }
                },
                "required": [
                    "username",
                    "displayname",
                    "roleId"
                ],
                "additionalProperties": False
            }
        },
        "projectMetaId": {
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
        }
    },
    "required": [
        "title",
        "description",
        "visibility",
        "members",
        "projectMetaId",
        "fields"
    ],
    "additionalProperties": False
}
