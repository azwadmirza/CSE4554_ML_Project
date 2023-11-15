def _get_items(query, server_id=None):

    ''' query = {
            'url': string,
            'params': dict -- opt, include StartIndex to resume
        }
    '''
    items = {
        'Items': [],
        'TotalRecordCount': 0,
        'RestorePoint': {}
    }

    url = query['url']
    query.setdefault('params', {})
    params = query['params']

    try:
        test_params = dict(params)
        test_params['Limit'] = 1
        test_params['EnableTotalRecordCount'] = True

        items['TotalRecordCount'] = _get(url, test_params, server_id=server_id)['TotalRecordCount']

    except Exception as error:
        LOG.exception("Failed to retrieve the server response %s: %s params:%s", url, error, params)

    else:
        params.setdefault('StartIndex', 0)

        def get_query_params(params, start, count):
            params_copy = dict(params)
            params_copy['StartIndex'] = start
            params_copy['Limit'] = count
            return params_copy

        query_params = [get_query_params(params, offset, LIMIT) \
                for offset in range(params['StartIndex'], items['TotalRecordCount'], LIMIT)]

        # multiprocessing.dummy.Pool completes all requests in multiple threads but has to
        # complete all tasks before allowing any results to be processed. ThreadPoolExecutor
        # allows for completed tasks to be processed while other tasks are completed on other
        # threads. Dont be a dummy.Pool, be a ThreadPoolExecutor
        import concurrent.futures
        p = concurrent.futures.ThreadPoolExecutor(DTHREADS)

        results = p.map(lambda params: _get(url, params, server_id=server_id), query_params)

        for params, result in zip(query_params, results):
            query['params'] = params

            result = result or {'Items': []}
            items['Items'].extend(result['Items'])
            # Using items to return data and communicate a restore point back to the callee is
            # a violation of the SRP. TODO: Seperate responsibilities.
            items['RestorePoint'] = query
            yield items
            del items['Items'][:]