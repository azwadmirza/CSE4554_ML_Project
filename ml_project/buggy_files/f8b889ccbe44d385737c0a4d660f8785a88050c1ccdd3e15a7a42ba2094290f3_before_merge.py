def get_email_status_json():
    answer=list()
    # UIanswer = list()
    tasks=helper.global_WorkerThread.get_taskstatus()
    if not current_user.role_admin():
        for task in tasks:
            if task['user'] == current_user.nickname:
                if task['formStarttime']:
                    task['starttime'] = format_datetime(task['formStarttime'], format='short', locale=get_locale())
                    task['formStarttime'] = ""
                else:
                    if 'starttime' not in task:
                        task['starttime'] = ""
                answer.append(task)
    else:
        for task in tasks:
            if task['formStarttime']:
                task['starttime'] = format_datetime(task['formStarttime'], format='short', locale=get_locale())
                task['formStarttime'] = ""
            else:
                if 'starttime' not in  task:
                    task['starttime'] = ""
        answer = tasks

    # UIanswer = copy.deepcopy(answer)
    answer = helper.render_task_status(answer)

    js=json.dumps(answer)
    response = make_response(js)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response