    def get_monkey_group(monkey):
        if len(set(monkey["ip_addresses"]).intersection(local_ip_addresses())) != 0:
            monkey_type = "island_monkey"
        else:
            monkey_type = "manual" if NodeService.get_monkey_manual_run(monkey) else "monkey"

        monkey_os = NodeService.get_monkey_os(monkey)
        monkey_running = "" if Monkey.get_single_monkey_by_id(monkey["_id"]).is_dead() else "_running"
        return "%s_%s%s" % (monkey_type, monkey_os, monkey_running)