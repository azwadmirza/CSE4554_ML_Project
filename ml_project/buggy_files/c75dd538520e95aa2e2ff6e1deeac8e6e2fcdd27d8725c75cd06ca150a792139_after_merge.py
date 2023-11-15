def add_policy(bundle):
    request_inputs = anchore_engine.apis.do_request_prep(request, default_params={})
    bodycontent = request_inputs['bodycontent']
    params = request_inputs['params']

    return_object = []
    httpcode = 500
    userId = request_inputs['userId']

    try:
        logger.debug('Adding policy')
        client = internal_client_for(CatalogClient, request_inputs['userId'])
        jsondata = json.loads(bodycontent)

        # schema check
        try:
            localconfig = anchore_engine.configuration.localconfig.get_config()
            user_auth = localconfig['system_user_auth']
            verify = localconfig.get('internal_ssl_verify', True)

            p_client = internal_client_for(PolicyEngineClient, userId=userId)
            response = p_client.validate_bundle(jsondata)
            if not response.get('valid', False):
                httpcode = 400
                return_object = anchore_engine.common.helpers.make_response_error('Bundle failed validation', in_httpcode=400, detail=response.get('validation_details'))
                return (return_object, httpcode)

        except Exception as err:
            raise Exception('Error response from policy service during bundle validation. Validation could not be performed: {}'.format(err))

        if 'id' in jsondata and jsondata['id']:
            policyId = jsondata['id']
        else:
            policyId = hashlib.md5(str(userId + ":" + jsondata['name']).encode('utf8')).hexdigest()
            jsondata['id'] = policyId

        try:
            policybundle = jsondata
            policy_record = client.add_policy(policybundle)
        except Exception as err:
            raise Exception("cannot store policy data to catalog - exception: " + str(err))

        if policy_record:
            return_object = make_response_policy(policy_record, params)
            httpcode = 200
        else:
            raise Exception('failed to add policy to catalog DB')
    except Exception as err:
        logger.debug("operation exception: " + str(err))
        return_object = anchore_engine.common.helpers.make_response_error(err, in_httpcode=httpcode)
        httpcode = return_object['httpcode']

    return (return_object, httpcode)