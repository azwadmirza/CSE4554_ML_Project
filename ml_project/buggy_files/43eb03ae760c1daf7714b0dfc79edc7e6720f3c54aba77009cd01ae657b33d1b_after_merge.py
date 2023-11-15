def main():
    # use the predefined argument spec for url
    argument_spec = url_argument_spec()
    # remove unnecessary arguments
    del argument_spec['force']
    del argument_spec['force_basic_auth']
    del argument_spec['http_agent']
    argument_spec.update(
        state=dict(choices=['present', 'absent', 'export'], default='present'),
        url=dict(aliases=['grafana_url'], required=True),
        url_username=dict(aliases=['grafana_user'], default='admin'),
        url_password=dict(aliases=['grafana_password'], default='admin', no_log=True),
        grafana_api_key=dict(type='str', no_log=True),
        org_id=dict(default=1, type='int'),
        folder=dict(type='str', default='General'),
        uid=dict(type='str'),
        slug=dict(type='str'),
        path=dict(type='str'),
        overwrite=dict(type='bool', default=False),
        commit_message=dict(type='str', aliases=['message'], deprecated_aliases=[dict(name='message', version='2.14')]),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_together=[['url_username', 'url_password', 'org_id']],
        mutually_exclusive=[['grafana_user', 'grafana_api_key'], ['uid', 'slug']],
    )

    if 'message' in module.params:
        module.fail_json(msg="'message' is reserved keyword, please change this parameter to 'commit_message'")

    try:
        if module.params['state'] == 'present':
            result = grafana_create_dashboard(module, module.params)
        elif module.params['state'] == 'absent':
            result = grafana_delete_dashboard(module, module.params)
        else:
            result = grafana_export_dashboard(module, module.params)
    except GrafanaAPIException as e:
        module.fail_json(
            failed=True,
            msg="error : %s" % to_native(e)
        )
        return
    except GrafanaMalformedJson as e:
        module.fail_json(
            failed=True,
            msg="error : %s" % to_native(e)
        )
        return
    except GrafanaDeleteException as e:
        module.fail_json(
            failed=True,
            msg="error : Can't delete dashboard : %s" % to_native(e)
        )
        return
    except GrafanaExportException as e:
        module.fail_json(
            failed=True,
            msg="error : Can't export dashboard : %s" % to_native(e)
        )
        return

    module.exit_json(
        failed=False,
        **result
    )
    return