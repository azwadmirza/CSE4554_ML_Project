def write_env(remote_info, uid):
    for_local_env = get_env_variables(remote_info)
    with open("/output/unproxied.env.tmp", "w") as f:
        for key, value in for_local_env.items():
            f.write("{}={}\n".format(key, value))
    chown("/output/unproxied.env.tmp", uid, uid)
    rename("/output/unproxied.env.tmp", "/output/unproxied.env")