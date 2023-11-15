def get_job_instance_log(request, biz_cc_id):
    client = get_client_by_request(request)
    job_instance_id = request.GET.get('job_instance_id')
    log_kwargs = {
        "bk_biz_id": biz_cc_id,
        "job_instance_id": job_instance_id
    }
    log_result = client.job.get_job_instance_log(log_kwargs)
    return JsonResponse(log_result)