    def create_container(self,
                         one_off=False,
                         previous_container=None,
                         number=None,
                         quiet=False,
                         **override_options):
        """
        Create a container for this service. If the image doesn't exist, attempt to pull
        it.
        """
        # This is only necessary for `scale` and `volumes_from`
        # auto-creating containers to satisfy the dependency.
        self.ensure_image_exists()

        container_options = self._get_container_create_options(
            override_options,
            number or self._next_container_number(one_off=one_off),
            one_off=one_off,
            previous_container=previous_container,
        )

        if 'name' in container_options and not quiet:
            log.info("Creating %s" % container_options['name'])

        try:
            return Container.create(self.client, **container_options)
        except APIError as ex:
            raise OperationFailedError("Cannot create container for service %s: %s" %
                                       (self.name, binarystr_to_unicode(ex.explanation)))