def wait_for_pod(remote_info):
    for i in range(120):
        phase = str(
            check_output([
                "kubectl", "get", "pod", remote_info.pod_name, "-o",
                "jsonpath={.status.phase}"
            ]), "utf-8"
        ).strip()
        if phase == "Running":
            return
        time.sleep(1)
    raise RuntimeError("Pod isn't starting: {}".format(phase))