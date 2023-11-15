    def start_loop(self):
        """Start the event loop."""
        connectors, databases, skills = \
            self.loader.load_modules_from_config(self.config)
        _LOGGER.debug("Loaded %i skills", len(skills))
        if databases is not None:
            self.start_databases(databases)
        self.setup_skills(skills)
        self.start_connector_tasks(connectors)
        self.eventloop.create_task(parse_crontab(self))
        self.web_server.start()
        try:
            pending = asyncio.Task.all_tasks()
            self.eventloop.run_until_complete(asyncio.gather(*pending))
        except RuntimeError as error:
            if str(error) != 'Event loop is closed':
                raise error
        finally:
            self.eventloop.close()