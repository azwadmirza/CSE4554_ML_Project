def job_get_job_task_detail(request, biz_cc_id, task_id):
    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_detail({'bk_biz_id': biz_cc_id,
                                            'bk_job_id': task_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板详情[app_id=%s]接口job.get_task_detail返回失败: %s") % (
            biz_cc_id, job_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    job_step_type_name = {
        1: _(u"脚本"),
        2: _(u"文件"),
        4: u"SQL"
    }
    task_detail = job_result['data']
    global_var = []
    steps = []
    for var in task_detail.get('global_vars', []):
        # 1-字符串, 2-IP, 3-索引数组, 4-关联数组
        if var['type'] in [JOB_VAR_TYPE_STR, JOB_VAR_TYPE_IP, JOB_VAR_TYPE_ARRAY]:
            value = var.get('value', '')
        else:
            value = ['{plat_id}:{ip}'.format(plat_id=ip_item['bk_cloud_id'], ip=ip_item['ip'])
                     for ip_item in var.get('ip_list', [])]
        global_var.append({
            'id': var['id'],
            # 全局变量类型：1:云参, 2:上下文参数，3:IP
            'category': var.get('category', 1),
            'name': var['name'],
            'type': var['type'],
            'value': value,
            'description': var['description']
        })
    for info in task_detail.get('steps', []):
        # 1-执行脚本, 2-传文件, 4-传SQL
        steps.append({
            'stepId': info['step_id'],
            'name': info['name'],
            'scriptParams': info.get('script_param', ''),
            'account': info.get('account', ''),
            'ipList': '',
            'type': info['type'],
            'type_name': job_step_type_name.get(info['type'], info['type'])
        })
    return JsonResponse({'result': True, 'data': {'global_var': global_var, 'steps': steps}})