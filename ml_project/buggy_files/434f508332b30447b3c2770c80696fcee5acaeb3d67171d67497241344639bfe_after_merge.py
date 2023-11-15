    def get_finding(self, resources, existing_finding_id, created_at, updated_at):
        policy = self.manager.ctx.policy
        model = self.manager.resource_type
        region = self.data.get('region', self.manager.config.region)

        if existing_finding_id:
            finding_id = existing_finding_id
        else:
            finding_id = '{}/{}/{}/{}'.format(
                self.manager.config.region,
                self.manager.config.account_id,
                hashlib.md5(json.dumps(
                    policy.data).encode('utf8')).hexdigest(),
                hashlib.md5(json.dumps(list(sorted(
                    [r[model.id] for r in resources]))).encode(
                        'utf8')).hexdigest())
        finding = {
            "SchemaVersion": self.FindingVersion,
            "ProductArn": "arn:aws:securityhub:{}:{}:product/{}/{}".format(
                region,
                self.manager.config.account_id,
                self.manager.config.account_id,
                self.ProductName,
            ),
            "AwsAccountId": self.manager.config.account_id,
            "Description": self.data.get(
                "description", policy.data.get("description", "")
            ).strip(),
            "Title": self.data.get("title", policy.name),
            'Id': finding_id,
            "GeneratorId": policy.name,
            'CreatedAt': created_at,
            'UpdatedAt': updated_at,
            "RecordState": "ACTIVE",
        }

        severity = {'Product': 0, 'Normalized': 0}
        if self.data.get("severity") is not None:
            severity["Product"] = self.data["severity"]
        if self.data.get("severity_normalized") is not None:
            severity["Normalized"] = self.data["severity_normalized"]
        if severity:
            finding["Severity"] = severity

        recommendation = {}
        if self.data.get("recommendation"):
            recommendation["Text"] = self.data["recommendation"]
        if self.data.get("recommendation_url"):
            recommendation["Url"] = self.data["recommendation_url"]
        if recommendation:
            finding["Remediation"] = {"Recommendation": recommendation}

        if "confidence" in self.data:
            finding["Confidence"] = self.data["confidence"]
        if "criticality" in self.data:
            finding["Criticality"] = self.data["criticality"]
        if "compliance_status" in self.data:
            finding["Compliance"] = {"Status": self.data["compliance_status"]}

        fields = {
            'resource': policy.resource_type,
            'ProviderName': 'CloudCustodian',
            'ProviderVersion': version
        }

        if "fields" in self.data:
            fields.update(self.data["fields"])
        else:
            tags = {}
            for t in policy.tags:
                if ":" in t:
                    k, v = t.split(":", 1)
                else:
                    k, v = t, ""
                tags[k] = v
            fields.update(tags)
        if fields:
            finding["ProductFields"] = fields

        finding_resources = []
        for r in resources:
            finding_resources.append(self.format_resource(r))
        finding["Resources"] = finding_resources
        finding["Types"] = list(self.data["types"])

        return filter_empty(finding)