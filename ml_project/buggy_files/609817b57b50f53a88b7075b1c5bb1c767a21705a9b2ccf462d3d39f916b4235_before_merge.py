    def _check_vxlan():
        interface_options = __salt__['openvswitch.interface_get_options'](name)
        interface_type = __salt__['openvswitch.interface_get_type'](name)
        if not 0 <= id <= 2**64:
            ret['result'] = False
            ret['comment'] = comment_vxlan_invalid_id
        elif not __salt__['dig.check_ip'](remote):
            ret['result'] = False
            ret['comment'] = comment_invalid_ip
        elif interface_options and interface_type and name in port_list:
            opt_port = 'dst_port=\"' + str(dst_port) + '\", ' if 0 < dst_port <= 65535 else ''
            interface_attroptions = '{{{0}key=\"'.format(opt_port) + str(id) + '\", remote_ip=\"' + str(remote) + '\"}'
            try:
                if interface_type[0] == 'vxlan' and interface_options[0] == interface_attroptions:
                    ret['result'] = True
                    ret['comment'] = comment_vxlan_interface_exists
            except KeyError:
                pass