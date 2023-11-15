def render_task_status(tasklist):
    renderedtasklist=list()
    for task in tasklist:
        if task['user'] == current_user.nickname or current_user.role_admin():
            if task['formStarttime']:
                task['starttime'] = format_datetime(task['formStarttime'], format='short', locale=web.get_locale())
            else:
                if 'starttime' not in task:
                    task['starttime'] = ""

            if 'formRuntime' not in task:
                task['runtime'] = ""
            else:
                task['runtime'] = format_runtime(task['formRuntime'])

            # localize the task status
            if isinstance( task['stat'], int ):
                if task['stat'] == worker.STAT_WAITING:
                    task['status'] = _(u'Waiting')
                elif task['stat'] == worker.STAT_FAIL:
                    task['status'] = _(u'Failed')
                elif task['stat'] == worker.STAT_STARTED:
                    task['status'] = _(u'Started')
                elif task['stat'] == worker.STAT_FINISH_SUCCESS:
                    task['status'] = _(u'Finished')
                else:
                    task['status'] = _(u'Unknown Status')

            # localize the task type
            if isinstance( task['taskType'], int ):
                if task['taskType'] == worker.TASK_EMAIL:
                    task['taskMessage'] = _(u'E-mail: ') + task['taskMess']
                elif  task['taskType'] == worker.TASK_CONVERT:
                    task['taskMessage'] = _(u'Convert: ') + task['taskMess']
                elif  task['taskType'] == worker.TASK_UPLOAD:
                    task['taskMessage'] = _(u'Upload: ') + task['taskMess']
                elif  task['taskType'] == worker.TASK_CONVERT_ANY:
                    task['taskMessage'] = _(u'Convert: ') + task['taskMess']
                else:
                    task['taskMessage'] = _(u'Unknown Task: ') + task['taskMess']

            renderedtasklist.append(task)

    return renderedtasklist