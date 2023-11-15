    def format_yaml(obj):
        from yaml import (safe_dump, representer)
        import json

        try:
            return safe_dump(obj.result, default_flow_style=False)
        except representer.RepresenterError:
            # yaml.safe_dump fails when obj.result is an OrderedDict. knack's --query implementation converts the result to an OrderedDict. https://github.com/microsoft/knack/blob/af674bfea793ff42ae31a381a21478bae4b71d7f/knack/query.py#L46. # pylint: disable=line-too-long
            return safe_dump(json.loads(json.dumps(obj.result)), default_flow_style=False)