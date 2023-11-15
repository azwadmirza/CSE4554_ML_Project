def init_api_resources(api):
    api.add_resource(Root, '/api')
    api.add_resource(Monkey, '/api/monkey', '/api/monkey/', '/api/monkey/<string:guid>')
    api.add_resource(LocalRun, '/api/local-monkey', '/api/local-monkey/')
    api.add_resource(ClientRun, '/api/client-monkey', '/api/client-monkey/')
    api.add_resource(Telemetry, '/api/telemetry', '/api/telemetry/', '/api/telemetry/<string:monkey_guid>')
    api.add_resource(MonkeyConfiguration, '/api/configuration', '/api/configuration/')
    api.add_resource(IslandConfiguration, '/api/configuration/island', '/api/configuration/island/')
    api.add_resource(MonkeyDownload, '/api/monkey/download', '/api/monkey/download/',
                     '/api/monkey/download/<string:path>')
    api.add_resource(NetMap, '/api/netmap', '/api/netmap/')
    api.add_resource(Edge, '/api/netmap/edge', '/api/netmap/edge/')
    api.add_resource(Node, '/api/netmap/node', '/api/netmap/node/')

    # report_type: zero_trust or security
    api.add_resource(
        Report,
        '/api/report/<string:report_type>',
        '/api/report/<string:report_type>/<string:report_data>')

    api.add_resource(TelemetryFeed, '/api/telemetry-feed', '/api/telemetry-feed/')
    api.add_resource(Log, '/api/log', '/api/log/')
    api.add_resource(IslandLog, '/api/log/island/download', '/api/log/island/download/')
    api.add_resource(PBAFileDownload, '/api/pba/download/<string:path>')
    api.add_resource(FileUpload, '/api/fileUpload/<string:file_type>',
                     '/api/fileUpload/<string:file_type>?load=<string:filename>',
                     '/api/fileUpload/<string:file_type>?restore=<string:filename>')
    api.add_resource(RemoteRun, '/api/remote-monkey', '/api/remote-monkey/')
    api.add_resource(AttackConfiguration, '/api/attack')
    api.add_resource(AttackReport, '/api/attack/report')
    api.add_resource(VersionUpdate, '/api/version-update', '/api/version-update/')

    api.add_resource(MonkeyTest, '/api/test/monkey')
    api.add_resource(ClearCaches, '/api/test/clear_caches')
    api.add_resource(LogTest, '/api/test/log')