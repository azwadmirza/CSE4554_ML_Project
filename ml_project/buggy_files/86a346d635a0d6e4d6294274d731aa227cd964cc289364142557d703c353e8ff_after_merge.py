def wait_for_pod(remote_info):
    for i in range(120):
        try:
            pod = loads(
                str(
                    check_output([
                        "kubectl", "get", "pod", remote_info.pod_name, "-o",
                        "json"
                    ]), "utf-8"
                )
            )
        except CalledProcessError:
            time.sleep(1)
            continue
        if pod["status"]["phase"] == "Running":
            for container in pod["status"]["containerStatuses"]:
                if container["name"] == remote_info.container_name and (
                    container["ready"]
                ):
                    return
        time.sleep(1)
    raise RuntimeError(
        "Pod isn't starting or can't be found: {}".format(pod["status"])
    )