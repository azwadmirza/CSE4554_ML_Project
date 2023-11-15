    def _create_domain_name_v2(self, api_args):
        # type: (Dict[str, Any]) -> DomainNameResponse
        client = self._client('apigatewayv2')
        exceptions = (
            client.exceptions.TooManyRequestsException,
        )
        result = self._call_client_method_with_retries(
            client.create_domain_name,
            api_args, max_attempts=6,
            should_retry=lambda x: True,
            retryable_exceptions=exceptions
        )
        result_data = result['DomainNameConfigurations'][0]
        domain_name = {
            'domain_name': result['DomainName'],
            'alias_domain_name': result_data['ApiGatewayDomainName'],
            'security_policy': result_data['SecurityPolicy'],
            'hosted_zone_id': result_data['HostedZoneId'],
            'certificate_arn': result_data['CertificateArn']
        }  # type: DomainNameResponse
        return domain_name