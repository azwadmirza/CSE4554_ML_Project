def _handle_concurrent_reply(fn, o, *args, **kwargs):
    # Make first call to o.reply a no op and start the script thread.
    # We must not start the script thread before, as this may lead to a nasty race condition
    # where the script thread replies a different response before the normal reply, which then gets swallowed.

    def run():
        fn(*args, **kwargs)
        # If the script did not call .reply(), we have to do it now.
        reply_proxy()

    script_thread = ScriptThread(target=run)

    reply_proxy = ReplyProxy(o.reply, script_thread)
    o.reply = reply_proxy