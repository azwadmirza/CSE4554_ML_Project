    def update_domain_name(self,
                           protocol,                  # type: str
                           domain_name,               # type: str
                           endpoint_type,             # type: str
                           certificate_arn,           # type: str
                           security_policy=None,      # type: Optional[str]
                           tags=None,                 # type: StrMap
                           ):
        # type: (...) -> Dict[str, Any]
        if protocol == 'HTTP':
            patch_operations = self.get_custom_domain_patch_operations(
                certificate_arn,
                endpoint_type,
                security_policy,
            )
            updated_domain_name = self._update_domain_name(
                domain_name, patch_operations
            )
        elif protocol == 'WEBSOCKET':
            kwargs = self.get_custom_domain_params_v2(
                domain_name=domain_name,
                endpoint_type=endpoint_type,
                security_policy=security_policy,
                certificate_arn=certificate_arn,
            )
            updated_domain_name = self._update_domain_name_v2(kwargs)
        else:
            raise ValueError('Unsupported protocol value.')
        resource_arn = 'arn:aws:apigateway:{region_name}:' \
                       ':/domainnames/{domain_name}'\
            .format(
                region_name=self.region_name,
                domain_name=domain_name
            )
        self._update_resource_tags(resource_arn, tags)
        return updated_domain_name