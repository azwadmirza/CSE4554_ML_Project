def custom_format(slither, result):
    elements = result["elements"]
    for element in elements:
        if element["type"] != "function":
            # Skip variable elements
            continue
        target_contract = slither.get_contract_from_name(
            element["type_specific_fields"]["parent"]["name"]
        )
        if target_contract:
            function = target_contract.get_function_from_signature(
                element["type_specific_fields"]["signature"]
            )
            if function:
                _patch(
                    slither,
                    result,
                    element["source_mapping"]["filename_absolute"],
                    int(
                        function.parameters_src().source_mapping["start"]
                        + function.parameters_src().source_mapping["length"]
                    ),
                    int(function.returns_src().source_mapping["start"]),
                )