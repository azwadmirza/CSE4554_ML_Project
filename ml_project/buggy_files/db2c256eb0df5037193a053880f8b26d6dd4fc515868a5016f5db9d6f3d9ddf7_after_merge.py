    def update(self, event_id, service_id, data):
        data = self.validate(data, event_id, check_required=False)
        data_copy = data.copy()
        data_copy = self.fix_payload_post(event_id, data_copy)
        data = self._delete_fields(data)
        session = DataGetter.get_session(service_id)  # session before any updates are made
        obj = ServiceDAO.update(self, event_id, service_id, data, validate=False)  # session after update

        if 'state' in data:
            if data['state'] == 'pending' and session.state == 'draft':
                trigger_new_session_notifications(session.id, event_id=event_id)

            if (data['state'] == 'accepted' and session.state != 'accepted') \
                    or (data['state'] == 'rejected' and session.state != 'rejected'):
                trigger_session_state_change_notifications(obj, event_id=event_id, state=data['state'])

        if session.start_time != obj.start_time or session.end_time != obj.end_time:
            trigger_session_schedule_change_notifications(obj, event_id)

        for f in ['track', 'microlocation', 'speakers', 'session_type']:
            if f in data_copy:
                setattr(obj, f, data_copy[f])
        obj = save_db_model(obj, SessionModel.__name__, event_id)
        return obj