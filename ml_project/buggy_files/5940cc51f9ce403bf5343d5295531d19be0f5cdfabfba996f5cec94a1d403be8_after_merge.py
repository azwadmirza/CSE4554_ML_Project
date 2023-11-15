def api_rule_matcher(api_findings, perms, data, file_path, api_rules):
    """Android API Analysis Rule Matcher"""
    try:
        for api in api_rules:

            # CASE CHECK
            if api["input_case"] == "lower":
                tmp_data = data.lower()
            elif api["input_case"] == "upper":
                tmp_data = data.upper()
            elif api["input_case"] == "exact":
                tmp_data = data

            # MATCH TYPE
            if api["type"] == "regex":
                if api["match"] == 'single_regex':
                    if re.findall(api["regex1"], tmp_data):
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'regex_and':
                    and_match_rgx = True
                    match_list = get_list_match_items(api)
                    for match in match_list:
                        if bool(re.findall(match, tmp_data)) is False:
                            and_match_rgx = False
                            break
                    if and_match_rgx:
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'regex_or':
                    match_list = get_list_match_items(api)
                    for match in match_list:
                        if re.findall(match, tmp_data):
                            add_apis(api_findings, api["desc"], file_path)
                            break
                elif api["match"] == 'regex_and_perm':
                    if (api["perm"] in perms) and (re.findall(api["regex1"], tmp_data)):
                        add_apis(api_findings, api["desc"], file_path)
                else:
                    logger.error("API Regex Rule Match Error\n" + api)

            elif api["type"] == "string":
                if api["match"] == 'single_string':
                    if api["string1"] in tmp_data:
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'string_and':
                    and_match_str = True
                    match_list = get_list_match_items(api)
                    for match in match_list:
                        if (match in tmp_data) is False:
                            and_match_str = False
                            break
                    if and_match_str:
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'string_or':
                    match_list = get_list_match_items(api)
                    for match in match_list:
                        if match in tmp_data:
                            add_apis(api_findings, api["desc"], file_path)
                            break
                elif api["match"] == 'string_and_or':
                    match_list = get_list_match_items(api)
                    string_or_stat = False
                    for match in match_list:
                        if match in tmp_data:
                            string_or_stat = True
                            break
                    if string_or_stat and (api["string1"] in tmp_data):
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'string_or_and':
                    match_list = get_list_match_items(api)
                    string_and_stat = True
                    for match in match_list:
                        if match in tmp_data is False:
                            string_and_stat = False
                            break
                    if string_and_stat or (api["string1"] in tmp_data):
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'string_and_perm':
                    if (api["perm"] in perms) and (api["string1"] in tmp_data):
                        add_apis(api_findings, api["desc"], file_path)
                elif api["match"] == 'string_or_and_perm':
                    match_list = get_list_match_items(api)
                    string_or_ps = False
                    for match in match_list:
                        if match in tmp_data:
                            string_or_ps = True
                            break
                    if (api["perm"] in perms) and string_or_ps:
                        add_apis(api_findings, api["desc"], file_path)
                else:
                    logger.error("API String Rule Match Error\n%s", api)
            else:
                logger.error("API Rule Error\n%s", api)
    except:
        PrintException("Error in API Rule Processing")