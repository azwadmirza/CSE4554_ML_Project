    def db_writer_thread(self):
        num_frames = 0
        last_write = time.time()
        self._create_db()

        while not self.stop_running_event.is_set():
            messages = []

            m = self.get_message(self.GET_MESSAGE_TIMEOUT)
            while m is not None:
                log.debug("sqlitewriter buffering message")

                messages.append((
                    m.timestamp,
                    m.arbitration_id,
                    m.id_type,
                    m.is_remote_frame,
                    m.is_error_frame,
                    m.dlc,
                    buffer(m.data)
                ))
                m = self.get_message(self.GET_MESSAGE_TIMEOUT)

                if time.time() - last_write > self.MAX_TIME_BETWEEN_WRITES:
                    log.debug("Max timeout between writes reached")
                    break

            if len(messages) > 0:
                with self.conn:
                    log.debug("Writing %s frames to db", len(messages))
                    self.conn.executemany(SqliteWriter.insert_msg_template, messages)
                    num_frames += len(messages)
                    last_write = time.time()

        self.conn.close()
        log.info("Stopped sqlite writer after writing %s messages", num_frames)