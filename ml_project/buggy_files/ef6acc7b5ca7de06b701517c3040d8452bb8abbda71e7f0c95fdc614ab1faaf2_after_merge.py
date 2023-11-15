    def consume_events(self):
        # discover new events and ingest them
        events_path = self.path_to('artifacts', self.ident, 'job_events')

        # it's possible that `events_path` doesn't exist *yet*, because runner
        # hasn't actually written any events yet (if you ran e.g., a sleep 30)
        # only attempt to consume events if any were rsynced back
        if os.path.exists(events_path):
            for event in set(os.listdir(events_path)) - self.handled_events:
                path = os.path.join(events_path, event)
                if os.path.exists(path) and os.path.isfile(path):
                    try:
                        event_data = json.load(
                            open(os.path.join(events_path, event), 'r')
                        )
                    except json.decoder.JSONDecodeError:
                        # This means the event we got back isn't valid JSON
                        # that can happen if runner is still partially
                        # writing an event file while it's rsyncing
                        # these event writes are _supposed_ to be atomic
                        # but it doesn't look like they actually are in
                        # practice
                        # in this scenario, just ignore this event and try it
                        # again on the next sync
                        continue
                    self.event_handler(event_data)
                    self.handled_events.add(event)