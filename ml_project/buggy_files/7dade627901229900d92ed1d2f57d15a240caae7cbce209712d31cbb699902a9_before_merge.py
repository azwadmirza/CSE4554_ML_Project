def state_absent(module, existing, proposed, candidate):
    commands = []
    parents = ["router bgp {0}".format(module.params['asn'])]
    if module.params['vrf'] != 'default':
        parents.append('vrf {0}'.format(module.params['vrf']))

    commands.append('no address-family {0} {1}'.format(
        module.params['afi'], module.params['safi']))
    candidate.add(commands, parents=parents)