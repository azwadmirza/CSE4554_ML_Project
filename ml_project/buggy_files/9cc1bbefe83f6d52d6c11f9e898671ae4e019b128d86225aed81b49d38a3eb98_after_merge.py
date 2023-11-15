    def _update_domain_name(self, custom_domain_name, patch_operations):
        # type: (str, List[Dict[str, str]]) -> DomainNameResponse
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

        if result.get('regionalCertificateArn'):
            certificate_arn = result['regionalCertificateArn']
        else:
            certificate_arn = result['certificateArn']

        if result.get('regionalHostedZoneId'):
            hosted_zone_id = result['regionalHostedZoneId']
        else:
            hosted_zone_id = result['distributionHostedZoneId']

        if result.get('regionalDomainName') is not None:
            alias_domain_name = result['regionalDomainName']
        else:
            alias_domain_name = result['distributionDomainName']
        domain_name = {
            'domain_name': result['domainName'],
            'security_policy': result['securityPolicy'],
            'certificate_arn': certificate_arn,
            'hosted_zone_id': hosted_zone_id,
            'alias_domain_name': alias_domain_name
        }  # type: DomainNameResponse
        return domain_name