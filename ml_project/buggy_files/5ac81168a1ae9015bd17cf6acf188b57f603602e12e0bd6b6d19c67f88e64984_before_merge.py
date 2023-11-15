def notify_snatch(ep_name, is_proper):
    for n in notifiers:
        n.notify_snatch(ep_name, is_proper)