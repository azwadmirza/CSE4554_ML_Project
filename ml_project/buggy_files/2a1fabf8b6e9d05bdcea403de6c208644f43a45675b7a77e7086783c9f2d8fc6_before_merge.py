    def housekeeping(expired_threshold=2, info_threshold=12):
        for (id, event, status, last_receive_id) in db.housekeeping(expired_threshold, info_threshold):
            if status == 'open':
                text = 'unshelved after timeout'
            elif status == 'expired':
                text = 'expired after timeout'
            else:
                text = 'alert timeout status change'
            history = History(
                id=last_receive_id,
                event=event,
                status=status,
                text=text,
                change_type="status",
                update_time=datetime.utcnow()
            )
            db.set_status(id, status, timeout=current_app.config['ALERT_TIMEOUT'], history=history)