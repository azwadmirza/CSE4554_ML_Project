    def _get_valid_object(cls, module_path: Path, object_name: Optional[str],
                          enum_failed: bool = False) -> Iterator[Any]:
        """
        Generator returning objects with matching object_type and object_name in the path given.
        :param module_path: absolute path to the module
        :param object_name: Class name of the object
        :param enum_failed: If True, will return None for modules which fail.
            Otherwise, failing modules are skipped.
        :return: generator containing matching objects
        """

        # Generate spec based on absolute path
        # Pass object_name as first argument to have logging print a reasonable name.
        spec = importlib.util.spec_from_file_location(object_name or "", str(module_path))
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore # importlib does not use typehints
        except (ModuleNotFoundError, SyntaxError) as err:
            # Catch errors in case a specific module is not installed
            logger.warning(f"Could not import {module_path} due to '{err}'")
            if enum_failed:
                return iter([None])

        valid_objects_gen = (
            obj for name, obj in inspect.getmembers(module, inspect.isclass)
            if ((object_name is None or object_name == name) and
                issubclass(obj, cls.object_type) and obj is not cls.object_type)
        )
        return valid_objects_gen