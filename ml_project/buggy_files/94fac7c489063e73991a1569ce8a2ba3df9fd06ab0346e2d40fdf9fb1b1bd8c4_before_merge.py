    def create_domain_name(self,
                           protocol,              # type: str
                           domain_name,           # type: str
                           endpoint_type,         # type: str
                           certificate_arn,       # type: str
                           security_policy=None,  # type: Optional[str]
                           tags=None,             # type: StrMap
                           ):
        # type: (...) -> Dict[str, Any]
        if protocol == 'HTTP':
            kwargs = {
                'domainName': domain_name,
                'endpointConfiguration': {
                    'types': [endpoint_type],
                },
            }
            if security_policy is not None:
                kwargs['securityPolicy'] = security_policy
            if endpoint_type == 'EDGE':
                kwargs['certificateArn'] = certificate_arn
            else:
                kwargs['regionalCertificateArn'] = certificate_arn
            if tags is not None:
                kwargs['tags'] = tags
            created_domain_name = self._create_domain_name(kwargs)
        elif protocol == 'WEBSOCKET':
            kwargs = self.get_custom_domain_params_v2(
                domain_name=domain_name,
                endpoint_type=endpoint_type,
                security_policy=security_policy,
                certificate_arn=certificate_arn,
                tags=tags
            )
            created_domain_name = self._create_domain_name_v2(kwargs)
        else:
            raise ValueError("Unsupported protocol value.")
        return created_domain_name