def vb_get_network_addresses(machine_name=None, machine=None):
    """
    TODO distinguish between private and public addresses

    A valid machine_name or a machine is needed to make this work!

    !!!
    Guest prerequisite: GuestAddition
    !!!

    Thanks to Shrikant Havale for the StackOverflow answer http://stackoverflow.com/a/29335390

    More information on guest properties: https://www.virtualbox.org/manual/ch04.html#guestadd-guestprops

    @param machine_name:
    @type machine_name: str
    @param machine:
    @type machine: IMachine
    @return: All the IPv4 addresses we could get
    @rtype: str[]
    """
    if machine_name:
        machine = vb_get_box().findMachine(machine_name)

    ip_addresses = []
    # We can't trust virtualbox to give us up to date guest properties if the machine isn't running
    # For some reason it may give us outdated (cached?) values
    if machine.state == _virtualboxManager.constants.MachineState_Running:
        try:
            total_slots = int(machine.getGuestPropertyValue('/VirtualBox/GuestInfo/Net/Count'))
        except ValueError:
            total_slots = 0
        for i in range(total_slots):
            try:
                address = machine.getGuestPropertyValue("/VirtualBox/GuestInfo/Net/{0}/V4/IP".format(i))
                if address:
                    ip_addresses.append(address)
            except Exception as e:
                log.debug(e.message)

    return ip_addresses