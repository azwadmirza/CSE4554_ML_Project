    def _handle_event(self, event, source_conn, other_conn, is_server):
        self.log(
            "HTTP2 Event from {}".format("server" if is_server else "client"),
            "debug",
            [repr(event)]
        )

        if hasattr(event, 'stream_id'):
            if is_server and event.stream_id % 2 == 1:
                eid = self.server_to_client_stream_ids[event.stream_id]
            else:
                eid = event.stream_id

        if isinstance(event, events.RequestReceived):
            headers = netlib.http.Headers([[k, v] for k, v in event.headers])
            self.streams[eid] = Http2SingleStreamLayer(self, eid, headers)
            self.streams[eid].timestamp_start = time.time()
            self.streams[eid].no_body = (event.stream_ended is not None)
            if event.priority_updated is not None:
                self.streams[eid].priority_weight = event.priority_updated.weight
                self.streams[eid].priority_depends_on = event.priority_updated.depends_on
                self.streams[eid].priority_exclusive = event.priority_updated.exclusive
                self.streams[eid].handled_priority_event = event.priority_updated
            self.streams[eid].start()
        elif isinstance(event, events.ResponseReceived):
            headers = netlib.http.Headers([[k, v] for k, v in event.headers])
            self.streams[eid].queued_data_length = 0
            self.streams[eid].timestamp_start = time.time()
            self.streams[eid].response_headers = headers
            self.streams[eid].response_arrived.set()
        elif isinstance(event, events.DataReceived):
            if self.config.body_size_limit and self.streams[eid].queued_data_length > self.config.body_size_limit:
                raise netlib.exceptions.HttpException("HTTP body too large. Limit is {}.".format(self.config.body_size_limit))
            self.streams[eid].data_queue.put(event.data)
            self.streams[eid].queued_data_length += len(event.data)
            source_conn.h2.safe_increment_flow_control(event.stream_id, event.flow_controlled_length)
        elif isinstance(event, events.StreamEnded):
            self.streams[eid].timestamp_end = time.time()
            self.streams[eid].data_finished.set()
        elif isinstance(event, events.StreamReset):
            self.streams[eid].zombie = time.time()
            if eid in self.streams and event.error_code == 0x8:
                if is_server:
                    other_stream_id = self.streams[eid].client_stream_id
                else:
                    other_stream_id = self.streams[eid].server_stream_id
                if other_stream_id is not None:
                    other_conn.h2.safe_reset_stream(other_stream_id, event.error_code)
        elif isinstance(event, events.RemoteSettingsChanged):
            new_settings = dict([(id, cs.new_value) for (id, cs) in six.iteritems(event.changed_settings)])
            other_conn.h2.safe_update_settings(new_settings)
        elif isinstance(event, events.ConnectionTerminated):
            if event.error_code == h2.errors.NO_ERROR:
                # Do not immediately terminate the other connection.
                # Some streams might be still sending data to the client.
                return False
            else:
                # Something terrible has happened - kill everything!
                self.client_conn.h2.close_connection(
                    error_code=event.error_code,
                    last_stream_id=event.last_stream_id,
                    additional_data=event.additional_data
                )
                self.client_conn.send(self.client_conn.h2.data_to_send())
                self._kill_all_streams()
                return False
        elif isinstance(event, events.PushedStreamReceived):
            # pushed stream ids should be unique and not dependent on race conditions
            # only the parent stream id must be looked up first
            parent_eid = self.server_to_client_stream_ids[event.parent_stream_id]
            with self.client_conn.h2.lock:
                self.client_conn.h2.push_stream(parent_eid, event.pushed_stream_id, event.headers)
                self.client_conn.send(self.client_conn.h2.data_to_send())

            headers = netlib.http.Headers([[k, v] for k, v in event.headers])
            self.streams[event.pushed_stream_id] = Http2SingleStreamLayer(self, event.pushed_stream_id, headers)
            self.streams[event.pushed_stream_id].timestamp_start = time.time()
            self.streams[event.pushed_stream_id].pushed = True
            self.streams[event.pushed_stream_id].parent_stream_id = parent_eid
            self.streams[event.pushed_stream_id].timestamp_end = time.time()
            self.streams[event.pushed_stream_id].request_data_finished.set()
            self.streams[event.pushed_stream_id].start()
        elif isinstance(event, events.PriorityUpdated):
            mapped_stream_id = event.stream_id
            if mapped_stream_id in self.streams and self.streams[mapped_stream_id].server_stream_id:
                # if the stream is already up and running and was sent to the server
                # use the mapped server stream id to update priority information
                mapped_stream_id = self.streams[mapped_stream_id].server_stream_id

            if eid in self.streams:
                if self.streams[eid].handled_priority_event is event:
                    # this event was already handled during stream creation
                    # HeadersFrame + Priority information as RequestReceived
                    return True
                self.streams[eid].priority_weight = event.weight
                self.streams[eid].priority_depends_on = event.depends_on
                self.streams[eid].priority_exclusive = event.exclusive

            with self.server_conn.h2.lock:
                self.server_conn.h2.prioritize(
                    mapped_stream_id,
                    weight=event.weight,
                    depends_on=self._map_depends_on_stream_id(mapped_stream_id, event.depends_on),
                    exclusive=event.exclusive
                )
                self.server_conn.send(self.server_conn.h2.data_to_send())
        elif isinstance(event, events.TrailersReceived):
            raise NotImplementedError("TrailersReceived not implemented")

        return True