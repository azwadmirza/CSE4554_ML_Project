    def from_json(cls, json_info):
        from ..util import parse_date
        
        info = {
            key: val
            for key, val in json_info.items()
            if key in cls.field_names()
        }
        try:
            info['updated'] = int(parse_date(info.get('updated'))) # Cast to int which comes with rounding down
        except (ValueError, TypeError):
            info['updated'] = None
        info['sources'] = info.get('sources') or []

        json_history = info.get('history') or {}
        cast_history = {}

        for method, method_history in json_history.items():
            cast_history[method] = []
            for json_result in method_history:
                assert isinstance(json_result, dict), 'Items in Link["history"][method] must be dicts'
                cast_result = ArchiveResult.from_json(json_result)
                cast_history[method].append(cast_result)

        info['history'] = cast_history
        return cls(**info)