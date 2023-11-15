def narrow_parameter(json: str) -> OptionalNarrowListT:

    data = ujson.loads(json)
    if not isinstance(data, list):
        raise ValueError("argument is not a list")
    if len(data) == 0:
        # The "empty narrow" should be None, and not []
        return None

    def convert_term(elem: Union[Dict[str, Any], List[str]]) -> Dict[str, Any]:

        # We have to support a legacy tuple format.
        if isinstance(elem, list):
            if (len(elem) != 2 or any(not isinstance(x, str) for x in elem)):
                raise ValueError("element is not a string pair")
            return dict(operator=elem[0], operand=elem[1])

        if isinstance(elem, dict):
            # Make sure to sync this list to frontend also when adding a new operator.
            # that supports user IDs. Relevant code is located in static/js/message_fetch.js
            # in handle_operators_supporting_id_based_api function where you will need to update
            # operators_supporting_id, or operators_supporting_ids array.
            operators_supporting_id = ['sender', 'group-pm-with', 'stream']
            operators_supporting_ids = ['pm-with']
            operators_non_empty_operand = {'search'}

            operator = elem.get('operator', '')
            if operator in operators_supporting_id:
                operand_validator = check_string_or_int
            elif operator in operators_supporting_ids:
                operand_validator = check_string_or_int_list
            elif operator in operators_non_empty_operand:
                operand_validator = check_required_string
            else:
                operand_validator = check_string

            validator = check_dict([
                ('operator', check_string),
                ('operand', operand_validator),
            ])

            error = validator('elem', elem)
            if error:
                raise JsonableError(error)

            # whitelist the fields we care about for now
            return dict(
                operator=elem['operator'],
                operand=elem['operand'],
                negated=elem.get('negated', False),
            )

        raise ValueError("element is not a dictionary")

    return list(map(convert_term, data))