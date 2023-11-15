def get_tasks_status():
    # if current user admin, show all email, otherwise only own emails
    answer=list()
    # UIanswer=list()
    tasks=helper.global_WorkerThread.get_taskstatus()
        # answer = tasks

    # UIanswer = copy.deepcopy(answer)
    answer = helper.render_task_status(tasks)
    # foreach row format row
    return render_title_template('tasks.html', entries=answer, title=_(u"Tasks"), page="tasks")