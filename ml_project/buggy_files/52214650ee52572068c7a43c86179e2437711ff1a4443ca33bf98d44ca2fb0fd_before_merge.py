def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_request(request)
    job_result = client.job.get_job_list({'bk_biz_id': biz_cc_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (
            biz_cc_id, job_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)
    task_list = []
    for task in job_result['data']:
        task_list.append({
            'value': task['bk_job_id'],
            'text': task['name'],
        })
    return JsonResponse({'result': True, 'data': task_list})