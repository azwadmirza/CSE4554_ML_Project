    def get_environment(self):
        def extract_temperature_data(data):
            for s in data:
                temp = s['currentTemperature'] if 'currentTemperature' in s else 0.0
                name = s['name']
                values = {
                   'temperature': temp,
                   'is_alert': temp > s['overheatThreshold'],
                   'is_critical': temp > s['criticalThreshold']
                }
                yield name, values

        sh_version_out = self.device.run_commands(['show version'])
        is_veos = sh_version_out[0]['modelName'].lower() == 'veos'
        commands = [
            'show environment cooling',
            'show environment temperature'
        ]
        if not is_veos:
            commands.append('show environment power')
            fans_output, temp_output, power_output = self.device.run_commands(commands)
        else:
            fans_output, temp_output = self.device.run_commands(commands)
        environment_counters = {
            'fans': {},
            'temperature': {},
            'power': {},
            'cpu': {}
        }
        cpu_output = self.device.run_commands(['show processes top once'],
                                              encoding='text')[0]['output']
        for slot in fans_output['fanTraySlots']:
            environment_counters['fans'][slot['label']] = {'status': slot['status'] == 'ok'}
        # First check FRU's
        for fru_type in ['cardSlots', 'powerSupplySlots']:
            for fru in temp_output[fru_type]:
                t = {name: value for name, value in extract_temperature_data(fru['tempSensors'])}
                environment_counters['temperature'].update(t)
        # On board sensors
        parsed = {n: v for n, v in extract_temperature_data(temp_output['tempSensors'])}
        environment_counters['temperature'].update(parsed)
        if not is_veos:
            for psu, data in power_output['powerSupplies'].items():
                environment_counters['power'][psu] = {
                    'status': data.get('state', 'ok') == 'ok',
                    'capacity': data.get('capacity', -1.0),
                    'output': data.get('outputPower', -1.0),
                }
        cpu_lines = cpu_output.splitlines()
        # Matches either of
        # Cpu(s):  5.2%us,  1.4%sy,  0.0%ni, 92.2%id,  0.6%wa,  0.3%hi,  0.4%si,  0.0%st ( 4.16 > )
        # %Cpu(s):  4.2 us,  0.9 sy,  0.0 ni, 94.6 id,  0.0 wa,  0.1 hi,  0.2 si,  0.0 st ( 4.16 < )
        m = re.match('.*ni, (?P<idle>.*).id.*', cpu_lines[2])
        environment_counters['cpu'][0] = {
            '%usage': round(100 - float(m.group('idle')), 1)
        }
        # Matches either of
        # Mem:   3844356k total,  3763184k used,    81172k free,    16732k buffers ( 4.16 > )
        # KiB Mem:  32472080 total,  5697604 used, 26774476 free,   372052 buffers ( 4.16 < )
        mem_regex = (r'[^\d]*(?P<total>\d+)[k\s]+total,'
                     r'\s+(?P<used>\d+)[k\s]+used,'
                     r'\s+(?P<free>\d+)[k\s]+free,.*')
        m = re.match(mem_regex, cpu_lines[3])
        environment_counters['memory'] = {
            'available_ram': int(m.group('total')),
            'used_ram': int(m.group('used'))
        }
        return environment_counters