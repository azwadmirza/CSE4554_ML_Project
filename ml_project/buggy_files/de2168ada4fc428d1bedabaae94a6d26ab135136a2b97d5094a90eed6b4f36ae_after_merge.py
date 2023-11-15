    def add_alert(self, alert, noupdate: bool = False, **details):
        obj, created = self.alert_set.get_or_create(
            name=alert, defaults={"details": details}
        )

        # Automatically lock on error
        if created and self.auto_lock_error and alert in LOCKING_ALERTS:
            self.do_lock(user=None, lock=True)

        # Update details with exception of component removal
        if not created and not noupdate:
            obj.details = details
            obj.save()

        if ALERTS[alert].link_wide:
            for component in self.linked_childs:
                component.add_alert(alert, noupdate=noupdate, **details)