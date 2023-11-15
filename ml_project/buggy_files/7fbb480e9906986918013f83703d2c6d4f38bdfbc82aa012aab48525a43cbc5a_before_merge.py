    def _check_gre():
        interface_options = __salt__['openvswitch.interface_get_options'](name)
        interface_type = __salt__['openvswitch.interface_get_type'](name)
        if not 0 <= id <= 2**32:
            ret['result'] = False
            ret['comment'] = comment_gre_invalid_id
        elif not __salt__['dig.check_ip'](remote):
            ret['result'] = False
            ret['comment'] = comment_invalid_ip
        elif interface_options and interface_type and name in port_list:
            interface_attroptions = '{key=\"' + str(id) + '\", remote_ip=\"' + str(remote) + '\"}'
            try:
                if interface_type[0] == 'gre' and interface_options[0] == interface_attroptions:
                    ret['result'] = True
                    ret['comment'] = comment_gre_interface_exists
            except KeyError:
                pass