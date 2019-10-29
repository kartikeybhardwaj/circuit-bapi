validate_add_meta_project_schema_1 = {
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
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\ ]*$",
                        "minLength": 4,
                        "maxLength": 20
                    },
                    "valueType": {
                        "type": "string",
                        "const": "select"
                    },
                    "value": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^[0-9a-zA-Z\-\ ]*$",
                            "minLength": 4,
                            "maxLength": 20
                        },
                        "minItems": 1,
                        "maxItems": 5,
                        "uniqueItems": True
                    }
                },
                "required": [
                    "key",
                    "valueType",
                    "value"
                ],
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 5,
            "uniqueItems": True
        }
    },
    "required": [
        "title",
        "description",
        "fields"
    ],
    "additionalProperties": False
}

validate_add_meta_project_schema_2 = {
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
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\ ]*$",
                        "minLength": 4,
                        "maxLength": 20
                    },
                    "valueType": {
                        "type": "string",
                        "const": "input"
                    },
                    "value": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\ ]*$",
                        "minLength": 0,
                        "maxLength": 20
                    }
                },
                "required": [
                    "key",
                    "valueType",
                    "value"
                ],
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 5,
            "uniqueItems": True
        }
    },
    "required": [
        "title",
        "description",
        "fields"
    ],
    "additionalProperties": False
}
