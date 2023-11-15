    def attach(self, engine: Engine, start: str = Events.STARTED,
               pause: str = Events.COMPLETED, resume: Optional[str] = None, step: Optional[str] = None) -> Timer:
        """ Register callbacks to control the timer.

        Args:
            engine (Engine):
                Engine that this timer will be attached to.
            start (Events):
                Event which should start (reset) the timer.
            pause (Events):
                Event which should pause the timer.
            resume (Events, optional):
                Event which should resume the timer.
            step (Events, optional):
                Event which should call the `step` method of the counter.

        Returns:
            self (Timer)

        """

        engine.add_event_handler(start, self.reset)
        engine.add_event_handler(pause, self.pause)

        if resume is not None:
            engine.add_event_handler(resume, self.resume)

        if step is not None:
            engine.add_event_handler(step, self.step)

        return self