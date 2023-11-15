def account_tags(account):
    tags = {'AccountName': account['name'], 'AccountId': account['account_id']}
    for t in account.get('tags', ()):
        if ':' not in t:
            continue
        k, v = t.split(':', 1)
        k = 'Account%s' % k.capitalize()
        tags[k] = v
    return tags