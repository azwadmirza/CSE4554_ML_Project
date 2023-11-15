    def driver_removed_handler(self, unused_channel, data):
        """Handle a notification that a driver has been removed.

        This releases any GPU resources that were reserved for that driver in
        Redis.
        """
        message = DriverTableMessage.GetRootAsDriverTableMessage(data, 0)
        driver_id = message.DriverId()
        log.info(
            "Driver {} has been removed.".format(binary_to_hex(driver_id)))

        # Get a list of the local schedulers that have not been deleted.
        local_schedulers = ray.global_state.local_schedulers()

        self._clean_up_entries_for_driver(driver_id)

        # Release any GPU resources that have been reserved for this driver in
        # Redis.
        for local_scheduler in local_schedulers:
            if local_scheduler.get("GPU", 0) > 0:
                local_scheduler_id = local_scheduler["DBClientID"]

                num_gpus_returned = 0

                # Perform a transaction to return the GPUs.
                with self.redis.pipeline() as pipe:
                    while True:
                        try:
                            # If this key is changed before the transaction
                            # below (the multi/exec block), then the
                            # transaction will not take place.
                            pipe.watch(local_scheduler_id)

                            result = pipe.hget(local_scheduler_id,
                                               "gpus_in_use")
                            gpus_in_use = (dict() if result is None else
                                           json.loads(result.decode("ascii")))

                            driver_id_hex = binary_to_hex(driver_id)
                            if driver_id_hex in gpus_in_use:
                                num_gpus_returned = gpus_in_use.pop(
                                    driver_id_hex)

                            pipe.multi()

                            pipe.hset(local_scheduler_id, "gpus_in_use",
                                      json.dumps(gpus_in_use))

                            pipe.execute()
                            # If a WatchError is not raise, then the operations
                            # should have gone through atomically.
                            break
                        except redis.WatchError:
                            # Another client must have changed the watched key
                            # between the time we started WATCHing it and the
                            # pipeline's execution. We should just retry.
                            continue

                log.info("Driver {} is returning GPU IDs {} to local "
                         "scheduler {}.".format(
                             binary_to_hex(driver_id), num_gpus_returned,
                             local_scheduler_id))