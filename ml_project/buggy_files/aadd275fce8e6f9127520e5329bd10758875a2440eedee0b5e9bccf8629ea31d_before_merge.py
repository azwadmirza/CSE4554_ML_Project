    async def process_notifications(login_obj, raw_notifications=None):
        """Process raw notifications json."""
        from alexapy import AlexaAPI

        if not raw_notifications:
            raw_notifications = await AlexaAPI.get_notifications(login_obj)
        email: Text = login_obj.email
        notifications = {"process_timestamp": datetime.utcnow()}
        for notification in raw_notifications:
            n_dev_id = notification.get("deviceSerialNumber")
            if n_dev_id is None:
                # skip notifications untied to a device for now
                # https://github.com/custom-components/alexa_media_player/issues/633#issuecomment-610705651
                continue
            n_type = notification["type"]
            if n_type == "MusicAlarm":
                n_type = "Alarm"
            n_id = notification["notificationIndex"]
            if n_type != "Timer":
                n_date = notification["originalDate"]
                n_time = notification["originalTime"]
                notification["date_time"] = f"{n_date} {n_time}"
            if n_dev_id not in notifications:
                notifications[n_dev_id] = {}
            if n_type not in notifications[n_dev_id]:
                notifications[n_dev_id][n_type] = {}
            notifications[n_dev_id][n_type][n_id] = notification
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["notifications"] = notifications
        _LOGGER.debug(
            "%s: Updated %s notifications for %s devices at %s",
            hide_email(email),
            len(raw_notifications),
            len(notifications),
            dt.as_local(
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["notifications"][
                    "process_timestamp"
                ]
            ),
        )