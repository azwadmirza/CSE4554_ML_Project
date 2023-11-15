    def create(self, event_id, data, url):
        data = self.validate(data, event_id)
        payload = self.fix_payload_post(event_id, data)
        speakers = payload.pop('speakers', None)
        session, status_code, location = ServiceDAO.create(self, event_id, payload, url, validate=False)
        if speakers:
            session.speakers = speakers
            save_to_db(session)
        if session.state == 'pending':
            trigger_new_session_notifications(session.id, event_id=event_id)
        return session, status_code, location