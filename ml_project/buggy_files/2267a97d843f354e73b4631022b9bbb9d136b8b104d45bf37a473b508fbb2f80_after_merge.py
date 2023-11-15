    def get_invalidation(self, distribution_id, caller_reference):
        current_invalidation = {}
        # find all invalidations for the distribution
        try:
            paginator = self.client.get_paginator('list_invalidations')
            invalidations = paginator.paginate(DistributionId=distribution_id).build_full_result().get('InvalidationList', {}).get('Items', [])
            invalidation_ids = [inv['Id'] for inv in invalidations]
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e, msg="Error listing CloudFront invalidations.")

        # check if there is an invalidation with the same caller reference
        for inv_id in invalidation_ids:
            try:
                invalidation = self.client.get_invalidation(DistributionId=distribution_id, Id=inv_id)['Invalidation']
                caller_ref = invalidation.get('InvalidationBatch', {}).get('CallerReference')
            except (BotoCoreError, ClientError) as e:
                self.module.fail_json_aws(e, msg="Error getting Cloudfront invalidation {0}".format(inv_id))
            if caller_ref == caller_reference:
                current_invalidation = invalidation
                break

        current_invalidation.pop('ResponseMetadata', None)
        return current_invalidation