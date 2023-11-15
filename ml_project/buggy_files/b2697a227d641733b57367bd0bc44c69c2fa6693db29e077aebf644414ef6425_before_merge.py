    def process(self, resources, event=None):
        for r in resources:
            region = self.manager.config.region
            trail_arn = Arn.parse(r['TrailARN'])

            if (r.get('IsOrganizationTrail') and
                    self.manager.config.account_id != trail_arn.account_id):
                continue
            if r.get('HomeRegion') and r['HomeRegion'] != region:
                region = trail_arn.region
            if self.annotation_key in r:
                continue
            client = local_session(self.manager.session_factory).client(
                'cloudtrail', region_name=region)
            status = client.get_trail_status(Name=r['Name'])
            status.pop('ResponseMetadata')
            r[self.annotation_key] = status

        return super(Status, self).process(resources)