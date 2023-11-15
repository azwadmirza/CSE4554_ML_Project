    def search_all_objects(cls, directory: Path) -> List[Dict[str, Any]]:
        """
        Searches a directory for valid objects
        :param directory: Path to search
        :return: List of dicts containing 'name', 'class' and 'location' entires
        """
        logger.debug(f"Searching for {cls.object_type.__name__} '{directory}'")
        objects = []
        for entry in directory.iterdir():
            # Only consider python files
            if not str(entry).endswith('.py'):
                logger.debug('Ignoring %s', entry)
                continue
            module_path = entry.resolve()
            logger.debug(f"Path {module_path}")
            for obj in cls._get_valid_object(module_path, object_name=None):
                objects.append(
                    {'name': obj.__name__,
                     'class': obj,
                     'location': entry,
                     })
        return objects