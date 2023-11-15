def await_spot_requests(module, ec2, spot_requests, count):
    """
    Wait for a group of spot requests to be fulfilled, or fail.

    module: Ansible module object
    ec2: authenticated ec2 connection object
    spot_requests: boto.ec2.spotinstancerequest.SpotInstanceRequest object returned by ec2.request_spot_instances
    count: Total number of instances to be created by the spot requests

    Returns:
        list of instance ID's created by the spot request(s)
    """
    spot_wait_timeout = int(module.params.get('spot_wait_timeout'))
    wait_complete = time.time() + spot_wait_timeout

    spot_req_inst_ids = dict()
    while time.time() < wait_complete:
        reqs = ec2.get_all_spot_instance_requests()
        for sirb in spot_requests:
            if sirb.id in spot_req_inst_ids:
                continue
            for sir in reqs:
                if sir.id != sirb.id:
                    continue  # this is not our spot instance
                if sir.instance_id is not None:
                    spot_req_inst_ids[sirb.id] = sir.instance_id
                elif sir.state == 'open':
                    continue  # still waiting, nothing to do here
                elif sir.state == 'active':
                    continue  # Instance is created already, nothing to do here
                elif sir.state == 'failed':
                    module.fail_json(msg="Spot instance request %s failed with status %s and fault %s:%s" % (
                        sir.id, sir.status.code, sir.fault.code, sir.fault.message))
                elif sir.state == 'cancelled':
                    module.fail_json(msg="Spot instance request %s was cancelled before it could be fulfilled." % sir.id)
                elif sir.state == 'closed':
                    # instance is terminating or marked for termination
                    # this may be intentional on the part of the operator,
                    # or it may have been terminated by AWS due to capacity,
                    # price, or group constraints in this case, we'll fail
                    # the module if the reason for the state is anything
                    # other than termination by user. Codes are documented at
                    # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-bid-status.html
                    if sir.status.code == 'instance-terminated-by-user':
                        # do nothing, since the user likely did this on purpose
                        pass
                    else:
                        spot_msg = "Spot instance request %s was closed by AWS with the status %s and fault %s:%s"
                        module.fail_json(msg=spot_msg % (sir.id, sir.status.code, sir.fault.code, sir.fault.message))

        if len(spot_req_inst_ids) < count:
            time.sleep(5)
        else:
            return spot_req_inst_ids.values()
    module.fail_json(msg="wait for spot requests timeout on %s" % time.asctime())