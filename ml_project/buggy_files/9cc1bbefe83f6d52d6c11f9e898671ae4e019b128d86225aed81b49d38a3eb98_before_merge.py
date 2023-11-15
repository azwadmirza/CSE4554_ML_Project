    def _update_domain_name(self, custom_domain_name, patch_operations):
        # type: (str, List[Dict[str, str]]) -> Dict[str, Any]
        client = self._client('apigateway')
        exceptions = (
            client.exceptions.TooManyRequestsException,
        )
        result = {}
        for patch_operation in patch_operations:
            api_args = {
                'domainName': custom_domain_name,
                'patchOperations': [patch_operation]
            }
            response = self._call_client_method_with_retries(
                client.update_domain_name,
                api_args, max_attempts=6,
                should_retry=lambda x: True,
                retryable_exceptions=exceptions
            )
            result.update(response)

        domain_name = {
            'domain_name': result['domainName'],
            'endpoint_configuration': result['endpointConfiguration'],
            'security_policy': result['securityPolicy'],
        }
        if result.get('regionalCertificateArn'):
            domain_name['certificate_arn'] = result['regionalCertificateArn']
        else:
            domain_name['certificate_arn'] = result['certificateArn']

        if result.get('regionalHostedZoneId'):
            domain_name['hosted_zone_id'] = result['regionalHostedZoneId']
        else:
            domain_name['hosted_zone_id'] = result['distributionHostedZoneId']

        if result.get('regionalDomainName') is not None:
            domain_name['alias_domain_name'] = result['regionalDomainName']
        else:
            domain_name['alias_domain_name'] = result['distributionDomainName']
        return domain_name