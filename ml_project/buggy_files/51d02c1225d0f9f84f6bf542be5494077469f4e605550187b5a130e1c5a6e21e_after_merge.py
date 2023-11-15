def main():
    tls_map = {
        'tlsv1.2': ssl.PROTOCOL_TLSv1_2,
        'tlsv1.1': ssl.PROTOCOL_TLSv1_1,
    }

    module = AnsibleModule(
        argument_spec=dict(
            server=dict(default='localhost'),
            port=dict(default=1883, type='int'),
            topic=dict(required=True),
            payload=dict(required=True),
            client_id=dict(default=None),
            qos=dict(default="0", choices=["0", "1", "2"]),
            retain=dict(default=False, type='bool'),
            username=dict(default=None),
            password=dict(default=None, no_log=True),
            ca_cert=dict(default=None, type='path', aliases=['ca_certs']),
            client_cert=dict(default=None, type='path', aliases=['certfile']),
            client_key=dict(default=None, type='path', aliases=['keyfile']),
            tls_version=dict(default=None, choices=['tlsv1.1', 'tlsv1.2'])
        ),
        supports_check_mode=True
    )

    if not HAS_PAHOMQTT:
        module.fail_json(msg=missing_required_lib('paho-mqtt'), exception=PAHOMQTT_IMP_ERR)

    server = module.params.get("server", 'localhost')
    port = module.params.get("port", 1883)
    topic = module.params.get("topic")
    payload = module.params.get("payload")
    client_id = module.params.get("client_id", '')
    qos = int(module.params.get("qos", 0))
    retain = module.params.get("retain")
    username = module.params.get("username", None)
    password = module.params.get("password", None)
    ca_certs = module.params.get("ca_cert", None)
    certfile = module.params.get("client_cert", None)
    keyfile = module.params.get("client_key", None)
    tls_version = module.params.get("tls_version", None)

    if client_id is None:
        client_id = "%s_%s" % (socket.getfqdn(), os.getpid())

    if payload and payload == 'None':
        payload = None

    auth = None
    if username is not None:
        auth = {'username': username, 'password': password}

    tls = None
    if ca_certs is not None:
        if tls_version:
            tls_version = tls_map.get(tls_version, ssl.PROTOCOL_SSLv23)
        else:
            if LooseVersion(platform.python_version()) <= "3.5.2":
                # Specifying `None` on later versions of python seems sufficient to
                # instruct python to autonegotiate the SSL/TLS connection. On versions
                # 3.5.2 and lower though we need to specify the version.
                #
                # Note that this is an alias for PROTOCOL_TLS, but PROTOCOL_TLS was
                # not available until 3.5.3.
                tls_version = ssl.PROTOCOL_SSLv23

        tls = {
            'ca_certs': ca_certs,
            'certfile': certfile,
            'keyfile': keyfile,
            'tls_version': tls_version,
        }

    try:
        mqtt.single(
            topic,
            payload,
            qos=qos,
            retain=retain,
            client_id=client_id,
            hostname=server,
            port=port,
            auth=auth,
            tls=tls
        )
    except Exception as e:
        module.fail_json(
            msg="unable to publish to MQTT broker %s" % to_native(e),
            exception=traceback.format_exc()
        )

    module.exit_json(changed=False, topic=topic)