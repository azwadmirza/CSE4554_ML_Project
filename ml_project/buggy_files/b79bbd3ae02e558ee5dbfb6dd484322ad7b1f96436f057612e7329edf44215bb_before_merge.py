def code_rule_matcher(findings, perms, data, file_path, code_rules):
    """Android Static Analysis Rule Matcher"""
    try:
        for rule in code_rules:

            # CASE CHECK
            if rule["input_case"] == "lower":
                tmp_data = data.lower()
            elif rule["input_case"] == "upper":
                tmp_data = data.upper()
            elif rule["input_case"] == "exact":
                tmp_data = data

            # MATCH TYPE
            if rule["type"] == "regex":
                if rule["match"] == 'single_regex':
                    if re.findall(rule["regex1"], tmp_data):
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'regex_and':
                    and_match_rgx = True
                    match_list = get_list_match_items(rule)
                    for match in match_list:
                        if bool(re.findall(match, tmp_data)) is False:
                            and_match_rgx = False
                            break
                    if and_match_rgx:
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'regex_or':
                    match_list = get_list_match_items(rule)
                    for match in match_list:
                        if re.findall(match, tmp_data):
                            add_findings(findings, rule[
                                         "desc"], file_path, rule)
                            break
                elif rule["match"] == 'regex_and_perm':
                    if (rule["perm"] in perms) and (re.findall(rule["regex1"], tmp_data)):
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                else:
                    logger.error("Code Regex Rule Match Error\n" + rule)

            elif rule["type"] == "string":
                if rule["match"] == 'single_string':
                    if rule["string1"] in tmp_data:
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'string_and':
                    and_match_str = True
                    match_list = get_list_match_items(rule)
                    for match in match_list:
                        if (match in tmp_data) is False:
                            and_match_str = False
                            break
                    if and_match_str:
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'string_or':
                    match_list = get_list_match_items(rule)
                    for match in match_list:
                        if match in tmp_data:
                            add_findings(findings, rule[
                                         "desc"], file_path, rule)
                            break
                elif rule["match"] == 'string_and_or':
                    match_list = get_list_match_items(rule)
                    string_or_stat = False
                    for match in match_list:
                        if match in tmp_data:
                            string_or_stat = True
                            break
                    if string_or_stat and (rule["string1"] in tmp_data):
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'string_or_and':
                    match_list = get_list_match_items(rule)
                    string_and_stat = True
                    for match in match_list:
                        if match in tmp_data is False:
                            string_and_stat = False
                            break
                    if string_and_stat or (rule["string1"] in tmp_data):
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'string_and_perm':
                    if (rule["perm"] in perms) and (rule["string1"] in tmp_data):
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                elif rule["match"] == 'string_or_and_perm':
                    match_list = get_list_match_items(rule)
                    string_or_ps = False
                    for match in match_list:
                        if match in tmp_data:
                            string_or_ps = True
                            break
                    if (rule["perm"] in perms) and string_or_ps:
                        add_findings(findings, rule[
                                     "desc"], file_path, rule)
                else:
                    logger.error("Code String Rule Match Error\n%s", rule)
            else:
                logger.error("Code Rule Error\n%s", rule)
    except:
        PrintException("[ERROR] Error in Code Rule Processing")