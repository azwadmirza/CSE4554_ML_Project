def get_update_status():
    return updater_thread.get_available_updates(request.method)