    def create_container(self,
                         one_off=False,
                         insecure_registry=False,
                         do_build=True,
                         intermediate_container=None,
                         **override_options):
        """
        Create a container for this service. If the image doesn't exist, attempt to pull
        it.
        """
        container_options = self._get_container_create_options(
            override_options,
            one_off=one_off,
            intermediate_container=intermediate_container,
        )

        if (do_build and
                self.can_be_built() and
                not self.client.images(name=self.full_name)):
            self.build()

        try:
            return Container.create(self.client, **container_options)
        except APIError as e:
            if e.response.status_code == 404 and e.explanation and 'No such image' in str(e.explanation):
                self.pull(insecure_registry=insecure_registry)
                return Container.create(self.client, **container_options)
            raise