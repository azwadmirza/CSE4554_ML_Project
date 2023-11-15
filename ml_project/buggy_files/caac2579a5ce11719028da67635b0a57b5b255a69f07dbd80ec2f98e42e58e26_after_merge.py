def build(
    serviceName,
    version,
    http=None,
    discoveryServiceUrl=DISCOVERY_URI,
    developerKey=None,
    model=None,
    requestBuilder=HttpRequest,
    credentials=None,
    cache_discovery=True,
    cache=None,
    client_options=None,
    adc_cert_path=None,
    adc_key_path=None,
    num_retries=1,
):
    """Construct a Resource for interacting with an API.

  Construct a Resource object for interacting with an API. The serviceName and
  version are the names from the Discovery service.

  Args:
    serviceName: string, name of the service.
    version: string, the version of the service.
    http: httplib2.Http, An instance of httplib2.Http or something that acts
      like it that HTTP requests will be made through.
    discoveryServiceUrl: string, a URI Template that points to the location of
      the discovery service. It should have two parameters {api} and
      {apiVersion} that when filled in produce an absolute URI to the discovery
      document for that service.
    developerKey: string, key obtained from
      https://code.google.com/apis/console.
    model: googleapiclient.Model, converts to and from the wire format.
    requestBuilder: googleapiclient.http.HttpRequest, encapsulator for an HTTP
      request.
    credentials: oauth2client.Credentials or
      google.auth.credentials.Credentials, credentials to be used for
      authentication.
    cache_discovery: Boolean, whether or not to cache the discovery doc.
    cache: googleapiclient.discovery_cache.base.CacheBase, an optional
      cache object for the discovery documents.
    client_options: Mapping object or google.api_core.client_options, client
      options to set user options on the client. The API endpoint should be set
      through client_options. client_cert_source is not supported, client cert
      should be provided using client_encrypted_cert_source instead.
    adc_cert_path: str, client certificate file path to save the application
      default client certificate for mTLS. This field is required if you want to
      use the default client certificate.
    adc_key_path: str, client encrypted private key file path to save the
      application default client encrypted private key for mTLS. This field is
      required if you want to use the default client certificate.
    num_retries: Integer, number of times to retry discovery with
      randomized exponential backoff in case of intermittent/connection issues.

  Returns:
    A Resource object with methods for interacting with the service.

  Raises:
    google.auth.exceptions.MutualTLSChannelError: if there are any problems
      setting up mutual TLS channel.
  """
    params = {"api": serviceName, "apiVersion": version}

    if http is None:
        discovery_http = build_http()
    else:
        discovery_http = http

    for discovery_url in \
            _discovery_service_uri_options(discoveryServiceUrl, version):
        requested_url = uritemplate.expand(discovery_url, params)

        try:
            content = _retrieve_discovery_doc(
                requested_url, discovery_http, cache_discovery, cache,
                developerKey, num_retries=num_retries
            )
            return build_from_document(
                content,
                base=discovery_url,
                http=http,
                developerKey=developerKey,
                model=model,
                requestBuilder=requestBuilder,
                credentials=credentials,
                client_options=client_options,
                adc_cert_path=adc_cert_path,
                adc_key_path=adc_key_path,
            )
        except HttpError as e:
            if e.resp.status == http_client.NOT_FOUND:
                continue
            else:
                raise e

    raise UnknownApiNameOrVersion("name: %s  version: %s" % (serviceName, version))