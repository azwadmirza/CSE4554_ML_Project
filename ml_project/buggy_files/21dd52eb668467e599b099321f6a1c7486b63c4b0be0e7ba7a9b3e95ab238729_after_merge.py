    def _create_domain_name(self, api_args):
        # type: (Dict[str, Any]) -> DomainNameResponse
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
        if result.get('regionalHostedZoneId'):
            hosted_zone_id = result['regionalHostedZoneId']
        else:
            hosted_zone_id = result['distributionHostedZoneId']

        if result.get('regionalCertificateArn'):
            certificate_arn = result['regionalCertificateArn']
        else:
            certificate_arn = result['certificateArn']

        if result.get('regionalDomainName') is not None:
            alias_domain_name = result['regionalDomainName']
        else:
            alias_domain_name = result['distributionDomainName']
        domain_name = {
            'domain_name': result['domainName'],
            'security_policy': result['securityPolicy'],
            'hosted_zone_id': hosted_zone_id,
            'certificate_arn': certificate_arn,
            'alias_domain_name': alias_domain_name,
        }  # type: DomainNameResponse
        return domain_name