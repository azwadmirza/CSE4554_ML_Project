    def stop(self, error=False):
        """Stops this trial.

        Stops this trial, releasing all allocating resources. If stopping the
        trial fails, the run will be marked as terminated in error, but no
        exception will be thrown.

        Args:
            error (bool): Whether to mark this trial as terminated in error.
        """

        if error:
            self.status = Trial.ERROR
        else:
            self.status = Trial.TERMINATED

        try:
            if self.agent:
                self.agent.stop.remote()
                self.agent.__ray_terminate__.remote(
                    self.agent._ray_actor_id.id())
        except Exception:
            print("Error stopping agent:", traceback.format_exc())
            self.status = Trial.ERROR
        finally:
            self.agent = None