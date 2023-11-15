    def rulefromstring(cls, stringline):
        pattern = None

        rule_type = ''
        rule_control = ''
        rule_module_path = ''
        rule_module_args = ''
        complicated = False

        if '[' in stringline:
            pattern = re.compile(
                r"""([\-A-Za-z0-9_]+)\s*         # Rule Type
                    \[([A-Za-z0-9_=\s]+)\]\s*    # Rule Control
                    ([A-Za-z0-9/_\-\.]+)\s*         # Rule Path
                    ([A-Za-z0-9,_=<>\-\s\./]*)""",  # Rule Args
                re.X)
            complicated = True
        else:
            pattern = re.compile(
                r"""([@\-A-Za-z0-9_]+)\s*        # Rule Type
                    ([A-Za-z0-9_\-]+)\s*          # Rule Control
                    ([A-Za-z0-9/_\-\.]*)\s*        # Rule Path
                    ([A-Za-z0-9,_=<>\-\s\./]*)""",  # Rule Args
                re.X)

        result = pattern.match(stringline)
        rule_type = result.group(1)
        if complicated:
            rule_control = '[' + result.group(2) + ']'
        else:
            rule_control = result.group(2)
        rule_module_path = result.group(3)
        if result.group(4) is not None:
            rule_module_args = result.group(4)

        return cls(rule_type, rule_control, rule_module_path, rule_module_args)