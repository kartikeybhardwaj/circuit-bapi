validate_add_locations_schema = {
    "type": "object",
    "properties": {
        "names": {
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
        "names"
    ],
    "additionalProperties": False
}
