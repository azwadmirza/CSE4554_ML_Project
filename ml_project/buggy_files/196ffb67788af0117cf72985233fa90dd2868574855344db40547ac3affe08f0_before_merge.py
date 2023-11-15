def _check_zip_deployment_status(deployment_status_url, authorization):
    import requests
    import time
    num_trials = 1
    while num_trials < 10:
        time.sleep(15)
        response = requests.get(deployment_status_url, headers=authorization)
        res_dict = response.json()
        num_trials = num_trials + 1
        if res_dict['status'] == 5:
            logger.warning("Zip deployment failed status %s", res_dict['status_text'])
            break
        elif res_dict['status'] == 4:
            break
        logger.info(res_dict['progress'])  # show only in debug mode, customers seem to find this confusing
    # if the deployment is taking longer than expected
    if res_dict['status'] != 4:
        logger.warning("""Deployment is taking longer than expected. Please verify status at '%s'
            beforing launching the app""", deployment_status_url)
    return res_dict