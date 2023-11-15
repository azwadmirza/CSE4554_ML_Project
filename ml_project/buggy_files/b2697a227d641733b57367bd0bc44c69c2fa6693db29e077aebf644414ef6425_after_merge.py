    def process(self, resources, event=None):

        non_account_trails = set()

        for r in resources:
            region = self.manager.config.region
            trail_arn = Arn.parse(r['TrailARN'])

            if (r.get('IsOrganizationTrail') and
                    self.manager.config.account_id != trail_arn.account_id):
                non_account_trails.add(r['TrailARN'])
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

        if non_account_trails:
            self.log.warning(
                'found %d org cloud trail from different account that cant be processed',
                len(non_account_trails))
        return super(Status, self).process([
            r for r in resources if r['TrailARN'] not in non_account_trails])