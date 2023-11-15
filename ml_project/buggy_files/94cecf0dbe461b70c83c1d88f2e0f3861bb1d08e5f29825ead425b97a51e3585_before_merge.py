    def shutdown(self, checkpoint=True, gracetime=2.0, hacksessconfcheckpoint=True):
        """ Checkpoints the session and closes it, stopping the download engine.
        @param checkpoint Whether to checkpoint the Session state on shutdown.
        @param gracetime Time to allow for graceful shutdown + signoff (seconds).
        """
        # Has to be called from the reactor thread
        assert isInIOThread()

        @inlineCallbacks
        def on_early_shutdown_complete(_):
            """
            Callback that gets called when the early shutdown has been compelted.
            Continues the shutdown procedure that is dependant on the early shutdown.
            :param _: ignored parameter of the Deferred
            """
            yield self.checkpoint_shutdown(stop=True, checkpoint=checkpoint,
                                 gracetime=gracetime, hacksessconfcheckpoint=hacksessconfcheckpoint)
            if self.sqlite_db:
                self.sqlite_db.close()
            self.sqlite_db = None

        return self.lm.early_shutdown().addCallback(on_early_shutdown_complete)