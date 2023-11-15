    def housekeeping(expired_threshold=2, info_threshold=12):
        expired, unshelved = db.housekeeping(expired_threshold, info_threshold)

        for (id, event, last_receive_id) in expired:
            history = History(
                id=last_receive_id,
                event=event,
                status='expired',
                text='expired after timeout',
                change_type="status",
                update_time=datetime.utcnow()
            )
            db.set_status(id, 'expired', timeout=current_app.config['ALERT_TIMEOUT'], history=history)

        for (id, event, last_receive_id) in unshelved:
            history = History(
                id=last_receive_id,
                event=event,
                status='open',
                text='unshelved after timeout',
                change_type="status",
                update_time=datetime.utcnow()
            )
            db.set_status(id, 'open', timeout=current_app.config['ALERT_TIMEOUT'], history=history)