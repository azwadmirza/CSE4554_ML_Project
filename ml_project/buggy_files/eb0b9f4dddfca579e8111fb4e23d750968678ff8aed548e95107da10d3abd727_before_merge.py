    def handle_BucketWebsiteConfiguration(self, resource, item_value):
        website = {}
        if item_value['indexDocumentSuffix']:
            website['IndexDocument'] = {
                'Suffix': item_value['indexDocumentSuffix']}
        if item_value['errorDocument']:
            website['ErrorDocument'] = {
                'Key': item_value['errorDocument']}
        if item_value['redirectAllRequestsTo']:
            website['RedirectAllRequestsTo'] = {
                'HostName': item_value['redirectsAllRequestsTo']['hostName'],
                'Protocol': item_value['redirectsAllRequestsTo']['protocol']}
        for r in item_value['routingRules']:
            redirect = {}
            rule = {'Redirect': redirect}
            website.setdefault('RoutingRules', []).append(rule)
            if 'condition' in r:
                cond = {}
                for ck, rk in (
                    ('keyPrefixEquals', 'KeyPrefixEquals'),
                    ('httpErrorCodeReturnedEquals',
                     'HttpErrorCodeReturnedEquals')):
                    if r['condition'][ck]:
                        cond[rk] = r['condition'][ck]
                rule['Condition'] = cond
            for ck, rk in (
                    ('protocol', 'Protocol'),
                    ('hostName', 'HostName'),
                    ('replaceKeyPrefixWith', 'ReplaceKeyPrefixWith'),
                    ('replaceKeyWith', 'ReplaceKeyWith'),
                    ('httpRedirectCode', 'HttpRedirectCode')):
                if r['redirect'][ck]:
                    redirect[rk] = r['redirect'][ck]
        resource['Website'] = website