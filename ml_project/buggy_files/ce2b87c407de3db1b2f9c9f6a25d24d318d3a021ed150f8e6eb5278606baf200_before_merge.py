    def _dump_message(self, error_traceback, message: dict):
        if message is None or getattr(self.parameters, 'testing', False):
            return

        self.logger.info('Dumping message to dump file.')

        dump_file = os.path.join(self.parameters.logging_path, self.__bot_id + ".dump")

        timestamp = datetime.utcnow()
        timestamp = timestamp.isoformat()
        new_dump_data = {}
        new_dump_data[timestamp] = {}
        new_dump_data[timestamp]["bot_id"] = self.__bot_id
        new_dump_data[timestamp]["source_queue"] = self.__source_queues
        new_dump_data[timestamp]["traceback"] = error_traceback

        new_dump_data[timestamp]["message"] = message.serialize()

        if os.path.exists(dump_file):
            # existing dump
            mode = 'r+'
        else:
            # new dump file
            mode = 'w'
        with open(dump_file, mode) as fp:
            for i in range(60):
                try:
                    fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    if i == 0:
                        self.logger.warning('Dump file is locked, waiting up to 60s.')
                    time.sleep(1)
                else:
                    break
            else:
                raise ValueError('Dump file was locked for more than 60s, giving up now.')
            if mode == 'r+':
                dump_data = json.load(fp)
                dump_data.update(new_dump_data)
            else:
                dump_data = new_dump_data

            fp.seek(0)

            json.dump(dump_data, fp, indent=4, sort_keys=True)

        self.logger.debug('Message dumped.')