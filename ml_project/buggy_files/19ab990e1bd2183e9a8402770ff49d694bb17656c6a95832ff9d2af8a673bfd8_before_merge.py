    def _load_single_record(self, prefix_record_json_path):
        log.trace("loading prefix record %s", prefix_record_json_path)
        with open(prefix_record_json_path) as fh:
            json_data = json_load(fh.read())
        prefix_record = PrefixRecord(**json_data)
        self.__prefix_records[prefix_record.name] = prefix_record