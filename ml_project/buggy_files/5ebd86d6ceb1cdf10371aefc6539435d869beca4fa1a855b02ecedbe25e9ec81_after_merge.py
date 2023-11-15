    def stop_threads(self):
        stop_coroutines = []
        # Notify stopping
        if self.config[CONFIG_NOTIFICATION_INSTANCE].enabled(CONFIG_NOTIFICATION_GLOBAL_INFO):
            # To be improved with a full async implementation
            # To be done : "asyncio.run" --> replaced by a simple await
            # PR discussion : https://github.com/Drakkar-Software/OctoBot/pull/563#discussion_r248088266
            stop_coroutines.append(
                self.config[CONFIG_NOTIFICATION_INSTANCE].notify_with_all(NOTIFICATION_STOPPING_MESSAGE))

        self.logger.info("Stopping threads ...")

        if self.main_task_group:
            self.main_task_group.cancel()

        for thread in self.dispatchers_list:
            thread.stop()

        # stop services
        for service_instance in ServiceCreator.get_service_instances(self.config):
            try:
                service_instance.stop()
            except Exception as e:
                raise e

        # stop exchanges threads
        for exchange in self.exchanges_list.values():
            stop_coroutines.append(exchange.stop())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.run(get_gather_wrapper(stop_coroutines))

        self.logger.info("Threads stopped.")