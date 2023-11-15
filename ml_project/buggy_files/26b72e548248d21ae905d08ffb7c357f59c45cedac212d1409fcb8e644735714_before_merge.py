  def _load_config(self, host, client_id, namespace, other_client_id, other_client_secret, existing_token):
    config = kfp_server_api.configuration.Configuration()

    host = host or ''
    # Preprocess the host endpoint to prevent some common user mistakes.
    # This should only be done for non-IAP cases (when client_id is None). IAP requires preserving the protocol.
    if not client_id:
      host = re.sub(r'^(http|https)://', '', host).rstrip('/')

    if host:
      config.host = host

    token = None

    # "existing_token" is designed to accept token generated outside of SDK. Here is an example.
    #
    # https://cloud.google.com/functions/docs/securing/function-identity
    # https://cloud.google.com/endpoints/docs/grpc/service-account-authentication
    #
    # import requests
    # import kfp
    #
    # def get_access_token():
    #     url = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
    #     r = requests.get(url, headers={'Metadata-Flavor': 'Google'})
    #     r.raise_for_status()
    #     access_token = r.json()['access_token']
    #     return access_token
    #
    # client = kfp.Client(host='<KFPHost>', existing_token=get_access_token())
    #
    if existing_token:
      token = existing_token
    elif client_id:
      token = get_auth_token(client_id, other_client_id, other_client_secret)
    elif self._is_inverse_proxy_host(host):
      token = get_gcp_access_token()

    if token:
      config.api_key['authorization'] = token
      config.api_key_prefix['authorization'] = 'Bearer'
      return config

    if host:
      # if host is explicitly set with auth token, it's probably a port forward address.
      return config

    import kubernetes as k8s
    in_cluster = True
    try:
      k8s.config.load_incluster_config()
    except:
      in_cluster = False
      pass

    if in_cluster:
      config.host = Client.IN_CLUSTER_DNS_NAME.format(namespace)
      return config

    try:
      k8s.config.load_kube_config(client_configuration=config)
    except:
      print('Failed to load kube config.')
      return config

    if config.host:
      config.host = config.host + '/' + Client.KUBE_PROXY_PATH.format(namespace)
    return config