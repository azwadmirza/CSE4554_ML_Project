    def handle_BucketLifecycleConfiguration(self, resource, item_value):
        rules = []
        for r in item_value.get('rules'):
            rr = {}
            rules.append(rr)
            expiry = {}
            for ek, ck in (
                    ('Date', 'expirationDate'),
                    ('ExpiredObjectDeleteMarker', 'expiredObjectDeleteMarker'),
                    ('Days', 'expirationInDays')):
                if r[ck] and r[ck] != -1:
                    expiry[ek] = r[ck]
            if expiry:
                rr['Expiration'] = expiry

            transitions = []
            for t in (r.get('transitions') or ()):
                tr = {}
                for k in ('date', 'days', 'storageClass'):
                    if t[k]:
                        tr["%s%s" % (k[0].upper(), k[1:])] = t[k]
                transitions.append(tr)
            if transitions:
                rr['Transitions'] = transitions

            if r.get('abortIncompleteMultipartUpload'):
                rr['AbortIncompleteMultipartUpload'] = {
                    'DaysAfterInitiation': r[
                        'abortIncompleteMultipartUpload']['daysAfterInitiation']}
            if r.get('noncurrentVersionExpirationInDays'):
                rr['NoncurrentVersionExpiration'] = {
                    'NoncurrentDays': r['noncurrentVersionExpirationInDays']}

            nonc_transitions = []
            for t in (r.get('noncurrentVersionTransitions') or ()):
                nonc_transitions.append({
                    'NoncurrentDays': t['days'],
                    'StorageClass': t['storageClass']})
            if nonc_transitions:
                rr['NoncurrentVersionTransitions'] = nonc_transitions

            rr['Status'] = r['status']
            rr['ID'] = r['id']
            if r.get('prefix'):
                rr['Prefix'] = r['prefix']
            if 'filter' not in r or not r['filter']:
                continue

            if r['filter']['predicate']:
                rr['Filter'] = self.convertLifePredicate(r['filter']['predicate'])

        resource['Lifecycle'] = {'Rules': rules}