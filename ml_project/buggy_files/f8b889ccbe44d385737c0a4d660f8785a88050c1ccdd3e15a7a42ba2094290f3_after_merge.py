def get_email_status_json():
    tasks=helper.global_WorkerThread.get_taskstatus()
    answer = helper.render_task_status(tasks)
    js=json.dumps(answer, default=helper.json_serial)
    response = make_response(js)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response