    def _parse_parameters(
        entitiy_str: Text, sidx: int, eidx: int, user_input: Text
    ) -> List[Dict[Text, Any]]:
        if entitiy_str is None or not entitiy_str.strip():
            # if there is nothing to parse we will directly exit
            return []

        try:
            parsed_entities = json.loads(entitiy_str)
            if isinstance(parsed_entities, dict):
                return RegexInterpreter._create_entities(parsed_entities, sidx, eidx)
            else:
                raise Exception(
                    "Parsed value isn't a json object "
                    "(instead parser found '{}')"
                    ".".format(type(parsed_entities))
                )
        except Exception as e:
            logger.warning(
                "Invalid to parse arguments in line "
                "'{}'. Failed to decode parameters"
                "as a json object. Make sure the intent"
                "followed by a proper json object. "
                "Error: {}".format(user_input, e)
            )
            return []