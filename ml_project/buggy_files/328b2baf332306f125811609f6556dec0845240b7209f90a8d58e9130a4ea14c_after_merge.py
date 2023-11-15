    def _log(event):
        if "log_text" in event:
            if event["log_text"].startswith("DNSDatagramProtocol starting on "):
                return

            if event["log_text"].startswith("(UDP Port "):
                return

            if event["log_text"].startswith("Timing out client"):
                return

        # this is a workaround to make sure we don't get stack overflows when the
        # logging system raises an error which is written to stderr which is redirected
        # to the logging system, etc.
        if getattr(threadlocal, "active", False):
            # write the text of the event, if any, to the *real* stderr (which may
            # be redirected to /dev/null, but there's not much we can do)
            try:
                event_text = eventAsText(event)
                print("logging during logging: %s" % event_text, file=sys.__stderr__)
            except Exception:
                # gah.
                pass
            return

        try:
            threadlocal.active = True
            return observer(event)
        finally:
            threadlocal.active = False