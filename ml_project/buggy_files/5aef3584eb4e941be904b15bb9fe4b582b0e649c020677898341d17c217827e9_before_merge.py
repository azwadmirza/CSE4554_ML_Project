    def finish_job_fact_cache(self, destination, modification_times):
        for host in self._get_inventory_hosts():
            filepath = os.sep.join(map(str, [destination, host.name]))
            if not os.path.realpath(filepath).startswith(destination):
                system_tracking_logger.error('facts for host {} could not be cached'.format(smart_str(host.name)))
                continue
            if os.path.exists(filepath):
                # If the file changed since we wrote it pre-playbook run...
                modified = os.path.getmtime(filepath)
                if modified > modification_times.get(filepath, 0):
                    with codecs.open(filepath, 'r', encoding='utf-8') as f:
                        try:
                            ansible_facts = json.load(f)
                        except ValueError:
                            continue
                        host.ansible_facts = ansible_facts
                        host.ansible_facts_modified = now()
                        ansible_local_system_id = ansible_facts.get('ansible_local', {}).get('insights', {}).get('system_id', None)
                        ansible_facts_system_id = ansible_facts.get('insights', {}).get('system_id', None)
                        if ansible_local_system_id:
                            print("Setting local {}".format(ansible_local_system_id))
                            logger.debug("Insights system_id {} found for host <{}, {}> in"
                                         " ansible local facts".format(ansible_local_system_id,
                                                                       host.inventory.id,
                                                                       host.name))
                            host.insights_system_id = ansible_local_system_id
                        elif ansible_facts_system_id:
                            logger.debug("Insights system_id {} found for host <{}, {}> in"
                                         " insights facts".format(ansible_local_system_id,
                                                                  host.inventory.id,
                                                                  host.name))
                            host.insights_system_id = ansible_facts_system_id
                        host.save()
                        system_tracking_logger.info(
                            'New fact for inventory {} host {}'.format(
                                smart_str(host.inventory.name), smart_str(host.name)),
                            extra=dict(inventory_id=host.inventory.id, host_name=host.name,
                                       ansible_facts=host.ansible_facts,
                                       ansible_facts_modified=host.ansible_facts_modified.isoformat(),
                                       job_id=self.id))
            else:
                # if the file goes missing, ansible removed it (likely via clear_facts)
                host.ansible_facts = {}
                host.ansible_facts_modified = now()
                system_tracking_logger.info(
                    'Facts cleared for inventory {} host {}'.format(
                        smart_str(host.inventory.name), smart_str(host.name)))
                host.save()