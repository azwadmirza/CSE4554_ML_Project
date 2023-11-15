def check_cross_account(policy_text, allowed_accounts):
    """Find cross account access policy grant not explicitly allowed
    """
    if isinstance(policy_text, basestring):
        policy = json.loads(policy_text)
    else:
        policy = policy_text

    violations = []
    for s in policy['Statement']:

        principal_ok = True

        if s['Effect'] != 'Allow':
            continue

        # Highly suspect in an allow
        if 'NotPrincipal' in s:
            violations.append(s)
            continue
        # Does this wildcard
        if 'Principal' not in s:
            violations.append(s)
            continue

        # Skip relays for events to sns
        if 'Service' in s['Principal']:
            s['Principal'].pop('Service')
            if not s['Principal']:
                continue

        assert len(s['Principal']) == 1, "Too many principals %s" % s

        # At this point principal is required?
        p = (
            isinstance(s['Principal'], basestring) and s['Principal']
            or s['Principal']['AWS'])

        p = isinstance(p, basestring) and (p,) or p
        for pid in p:
            if pid == '*':
                principal_ok = False
            elif pid.startswith('arn:aws:iam::cloudfront:user'):
                continue
            else:
                account_id = _account(pid)
                if account_id not in allowed_accounts:
                    principal_ok = False

        if principal_ok:
            continue

        if 'Condition' not in s:
            violations.append(s)
            continue

        if 'StringEquals' in s['Condition']:
            # Default SNS Policy does this
            if 'AWS:SourceOwner' in s['Condition']['StringEquals']:
                so = s['Condition']['StringEquals']['AWS:SourceOwner']
                if not isinstance(so, list):
                    so = [so]
                so = [pso for pso in so if pso not in allowed_accounts]
                if not so:
                    principal_ok = True

            # Default keys in kms do this
            if 'kms:CallerAccount' in s['Condition']['StringEquals']:
                so = s['Condition']['StringEquals']['kms:CallerAccount']
                if so in allowed_accounts:
                    principal_ok = True

        ## BEGIN S3 WhiteList
        ## Note these are transient white lists for s3
        ## we need to refactor this to verify ip against a
        ## cidr white list, and verify vpce/vpc against the
        ## accounts.

            # For now allow vpce/vpc conditions as sufficient on s3
            if s['Condition']['StringEquals'].keys()[0] in (
                    "aws:sourceVpce", "aws:sourceVpce"):
                principal_ok = True

        if 'StringLike' in s['Condition']:
            # For now allow vpce/vpc conditions as sufficient on s3
            if s['Condition'][
                    'StringLike'].keys()[0].lower() == "aws:sourcevpce":
                principal_ok = True

        if 'ForAnyValue:StringLike' in s['Condition']:
            if s['Condition']['ForAnyValue:StringLike'].keys()[
                    0].lower() == 'aws:sourcevpce':
                principal_ok = True

        if 'IpAddress' in s['Condition']:
            principal_ok = True

        ## END S3 WhiteList

        if 'ArnEquals' in s['Condition']:
            # Other valid arn equals? / are invalids allowed?
            # duplicate block from below, inline closure func
            # would remove, but slower, else move to class eval
            principal_ok = True

            keys = ('aws:SourceArn', 'AWS:SourceArn')
            for k in keys:
                if k in s['Condition']['ArnEquals']:
                    v = s['Condition']['ArnEquals'][k]
            if v is None:
                violations.append(s)
            else:
                v = isinstance(v, basestring) and (v,) or v
                for arn in v:
                    aid = _account(arn)
                    if aid not in allowed_accounts:
                        violations.append(s)
        if 'ArnLike' in s['Condition']:
            # Other valid arn equals? / are invalids allowed?
            v = s['Condition']['ArnLike']['aws:SourceArn']
            v = isinstance(v, basestring) and (v,) or v
            principal_ok = True
            for arn in v:
                aid = _account(arn)
                if aid not in allowed_accounts:
                    violations.append(s)
        if not principal_ok:
            violations.append(s)
    return violations