    def _create_domain_name(self, api_args):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        client = self._client('apigateway')
        exceptions = (
            client.exceptions.TooManyRequestsException,
        )
        result = self._call_client_method_with_retries(
            client.create_domain_name,
            api_args, max_attempts=6,
            should_retry=lambda x: True,
            retryable_exceptions=exceptions
        )
        domain_name = {
            'domain_name': result['domainName'],
            'endpoint_configuration': result['endpointConfiguration'],
            'security_policy': result['securityPolicy'],
        }
        if result.get('regionalHostedZoneId'):
            domain_name['hosted_zone_id'] = result['regionalHostedZoneId']
        else:
            domain_name['hosted_zone_id'] = result['distributionHostedZoneId']

        if result.get('regionalCertificateArn'):
            domain_name['certificate_arn'] = result['regionalCertificateArn']
        else:
            domain_name['certificate_arn'] = result['certificateArn']

        if result.get('regionalDomainName') is not None:
            domain_name['alias_domain_name'] = result['regionalDomainName']
        else:
            domain_name['alias_domain_name'] = result['distributionDomainName']
        return domain_name