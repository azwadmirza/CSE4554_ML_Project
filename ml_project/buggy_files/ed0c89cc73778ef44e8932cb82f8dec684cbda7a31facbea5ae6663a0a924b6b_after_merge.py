    def from_json(cls, json_info, guess=False):
        from ..util import parse_date

        info = {
            key: val
            for key, val in json_info.items()
            if key in cls.field_names()
        }
        if guess:
            keys = info.keys()
            if "start_ts" not in keys:
                info["start_ts"], info["end_ts"] = cls.guess_ts(json_info)
            else:
                info['start_ts'] = parse_date(info['start_ts'])
                info['end_ts'] = parse_date(info['end_ts'])
            if "pwd" not in keys:
                info["pwd"] = str(Path(OUTPUT_DIR) / ARCHIVE_DIR_NAME / json_info["timestamp"])
            if "cmd_version" not in keys:
                info["cmd_version"] = "Undefined"
            if "cmd" not in keys:
                info["cmd"] = []
        else:
            info['start_ts'] = parse_date(info['start_ts'])
            info['end_ts'] = parse_date(info['end_ts'])
            info['cmd_version'] = info.get('cmd_version')
        if type(info["cmd"]) is str:
            info["cmd"] = [info["cmd"]]
        return cls(**info)