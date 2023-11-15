    def get_monkey_group(monkey):
        keywords = []
        if len(set(monkey["ip_addresses"]).intersection(local_ip_addresses())) != 0:
            keywords.extend(["island", "monkey"])
        else:
            monkey_type = "manual" if NodeService.get_monkey_manual_run(monkey) else "monkey"
            keywords.append(monkey_type)

        keywords.append(NodeService.get_monkey_os(monkey))
        if not Monkey.get_single_monkey_by_id(monkey["_id"]).is_dead():
            keywords.append("running")
        return NodeStates.get_by_keywords(keywords).value