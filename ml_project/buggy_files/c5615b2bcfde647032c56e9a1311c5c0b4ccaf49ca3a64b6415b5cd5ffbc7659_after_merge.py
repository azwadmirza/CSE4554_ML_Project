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
                stop_tasks = []
                stop_tasks.append(self.agent.stop.remote())
                stop_tasks.append(self.agent.__ray_terminate__.remote(
                    self.agent._ray_actor_id.id()))
                _, unfinished = ray.wait(
                        stop_tasks, num_returns=2, timeout=10000)
                if unfinished:
                    print(("Stopping %s Actor was unsuccessful, "
                           "but moving on...") % self)
        except Exception:
            print("Error stopping agent:", traceback.format_exc())
            self.status = Trial.ERROR
        finally:
            self.agent = None