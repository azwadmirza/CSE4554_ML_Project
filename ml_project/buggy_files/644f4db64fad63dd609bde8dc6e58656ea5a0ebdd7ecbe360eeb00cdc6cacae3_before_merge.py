    def nextEventMatchingMask_untilDate_inMode_dequeue_(self, mask, date, mode, dequeue):
        if self.inLiveResize():
            # Call the idle() method while we're stuck in a live resize event.
            from pyglet import app
            if app.event_loop is not None:
                app.event_loop.idle()

        event = send_super(self, 'nextEventMatchingMask:untilDate:inMode:dequeue:',
                           mask, date, mode, dequeue,
                           preventSuperclassRecursion=True,
                           argtypes=[NSUInteger, c_void_p, c_void_p, c_bool])

        if event.value is None:
            return 0
        else:
            return event.value