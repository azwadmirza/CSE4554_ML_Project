    def handle(self, *args, **options):

        interval = float(options.get("interval") or DEFAULT_PING_INTERVAL)
        checkrate = float(options.get("checkrate") or DEFAULT_PING_CHECKRATE)
        server = options.get("server") or DEFAULT_SERVER_URL

        self.started = datetime.now()

        while True:
            try:
                logger.info("Attempting a ping.")
                with vacuum_db_lock:
                    data = self.perform_ping(server)
                    logger.info("Ping succeeded! (response: {})".format(data))
                    if "id" in data:
                        self.perform_statistics(server, data["id"])
                logger.info("Sleeping for {} minutes.".format(interval))
                time.sleep(interval * 60)
                continue
            except ConnectionError:
                logger.warn("Ping failed (could not connect). Trying again in {} minutes.".format(checkrate))
            except Timeout:
                logger.warn("Ping failed (connection timed out). Trying again in {} minutes.".format(checkrate))
            except RequestException as e:
                logger.warn("Ping failed ({})! Trying again in {} minutes.".format(e, checkrate))
            time.sleep(checkrate * 60)