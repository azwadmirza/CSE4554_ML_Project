    def _handle_failure(self, error):
        logger.exception("Error in monitor loop")
        if self.autoscaler is not None and \
           os.environ.get("RAY_AUTOSCALER_FATESHARE_WORKERS", "") == "1":
            self.autoscaler.kill_workers()
            # Take down autoscaler workers if necessary.
            self.destroy_autoscaler_workers()

        # Something went wrong, so push an error to all current and future
        # drivers.
        message = f"The autoscaler failed with the following error:\n{error}"
        if _internal_kv_initialized():
            _internal_kv_put(DEBUG_AUTOSCALING_ERROR, message, overwrite=True)
        redis_client = ray._private.services.create_redis_client(
            args.redis_address, password=args.redis_password)
        from ray.utils import push_error_to_driver_through_redis
        push_error_to_driver_through_redis(
            redis_client, ray_constants.MONITOR_DIED_ERROR, message)