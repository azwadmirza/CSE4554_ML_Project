    def get_or_create_public_ip_address(self, ip_config):
        name = ip_config.get('public_ip_address_name')
        pip = self.get_public_ip_address(name)
        if not pip:
            params = self.network_models.PublicIPAddress(
                location=self.location,
                public_ip_allocation_method=ip_config.get('public_ip_allocation_method'),
            )
            try:
                poller = self.network_client.public_ip_addresses.create_or_update(self.resource_group, name, params)
                pip = self.get_poller_result(poller)
            except CloudError as exc:
                self.fail("Error creating {0} - {1}".format(name, str(exc)))
        return pip