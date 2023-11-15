    def _check_vlan():
        tag = __salt__['openvswitch.port_get_tag'](name)
        interfaces = __salt__['network.interfaces']()
        if not 0 <= id <= 4095:
            ret['result'] = False
            ret['comment'] = comment_vlan_invalid_id
        elif not internal and name not in interfaces:
            ret['result'] = False
            ret['comment'] = comment_vlan_invalid_name
        elif tag and name in port_list:
            try:
                if int(tag[0]) == id:
                    ret['result'] = True
                    ret['comment'] = comment_vlan_port_exists
            except (ValueError, KeyError):
                pass