    def _load_single_record(self, prefix_record_json_path):
        log.trace("loading prefix record %s", prefix_record_json_path)
        with open(prefix_record_json_path) as fh:
            try:
                json_data = json_load(fh.read())
            except JSONDecodeError:
                raise CorruptedEnvironmentError(self.prefix_path, prefix_record_json_path)

        prefix_record = PrefixRecord(**json_data)
        self.__prefix_records[prefix_record.name] = prefix_record