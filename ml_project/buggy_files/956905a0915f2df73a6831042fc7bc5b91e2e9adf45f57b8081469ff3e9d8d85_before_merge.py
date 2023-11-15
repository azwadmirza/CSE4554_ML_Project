    def augment(self, resources):
        for r in resources:
            r['Tags'] = r.pop('TagSet', [])
        return resources