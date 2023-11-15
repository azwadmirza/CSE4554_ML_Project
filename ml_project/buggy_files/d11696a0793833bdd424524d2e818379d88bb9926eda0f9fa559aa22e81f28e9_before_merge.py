def backoff_request(giveup=False, *args, **kwargs):
    attempt = 0
    result = None
    while not result:
        result = make_request(*args, **kwargs)
        RETRY=False

        if not result:
            RETRY=True
        if 'retry' in result.json() and result.json()['retry']:
            RETRY=True
        elif not 'retry' in result.json() or not result.json()['retry']:
            return result

        if RETRY:
            attempt += 1
            if giveup and attempt == config.max_retries:
                print_err("Request to %s failed %s times. Giving up" % (config.server, config.max_retries))
                return None
            jitter = random.randint(0,1000) / 1000 # jitter to reduce chance of locking
            current_sleep = min(config.backoff_max, config.backoff_base * 2 ** attempt) + jitter
            print_err("Request to %s failed. Waiting %s seconds before retrying." % (config.server, current_sleep))
            time.sleep(current_sleep)
    return result