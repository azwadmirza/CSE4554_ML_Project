        def on_early_shutdown_complete(_):
            """
            Callback that gets called when the early shutdown has been completed.
            Continues the shutdown procedure that is dependant on the early shutdown.
            :param _: ignored parameter of the Deferred
            """
            self.save_session_config()
            yield self.checkpoint_downloads()
            self.lm.shutdown_downloads()
            self.lm.network_shutdown()

            if self.sqlite_db:
                self.sqlite_db.close()
            self.sqlite_db = None