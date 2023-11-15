def _gen_master_def(image_name, model_file, argv, timestamp):
    master_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: "elasticdl-master-{timestamp}"
  labels:
    purpose: test-command
spec:
  containers:
  - name: "elasticdl-master-{timestamp}"
    image: "{image_name}"
    command: ["python"]
    args: [
        "-m", "elasticdl.master.main",
        "--worker_image", "{image_name}",
        "--model_file", "{m_file}"
    ]
    imagePullPolicy: IfNotPresent 
    env:
    - name: MY_POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
  restartPolicy: Never
""" .format(m_file=_m_file_in_docker(model_file), image_name=image_name, timestamp=timestamp)

    master_def = yaml.safe_load(master_yaml)

    # Build master arguments
    master_def['spec']['containers'][0]['args'].extend(argv)
    return master_def