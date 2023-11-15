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