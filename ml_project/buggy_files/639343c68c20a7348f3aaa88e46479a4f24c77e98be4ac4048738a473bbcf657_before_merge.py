def generate_tmp_kube_config(credential, namespace):
    host_input = credential.get_input('host')
    config = {
        "apiVersion": "v1",
        "kind": "Config",
        "preferences": {},
        "clusters": [
            {
                "name": host_input,
                "cluster": {
                    "server": host_input
                }
            }
        ],
        "users": [
            {
                "name": host_input,
                "user": {
                    "token": credential.get_input('bearer_token')
                }
            }
        ],
        "contexts": [
            {
                "name": host_input,
                "context": {
                    "cluster": host_input,
                    "user": host_input,
                    "namespace": namespace
                }
            }
        ],
        "current-context": host_input
    }

    if credential.get_input('verify_ssl'):
        config["clusters"][0]["cluster"]["certificate-authority-data"] = b64encode(
            credential.get_input('ssl_ca_cert').encode() # encode to bytes
        ).decode() # decode the base64 data into a str
    else:
        config["clusters"][0]["cluster"]["insecure-skip-tls-verify"] = True
    return config