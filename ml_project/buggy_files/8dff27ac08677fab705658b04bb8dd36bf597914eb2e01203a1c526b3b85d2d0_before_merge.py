    def from_json(cls, json_info):
        from ..util import parse_date

        info = {
            key: val
            for key, val in json_info.items()
            if key in cls.field_names()
        }
        info['start_ts'] = parse_date(info['start_ts'])
        info['end_ts'] = parse_date(info['end_ts'])
        info['cmd_version'] = info.get('cmd_version')
        return cls(**info)