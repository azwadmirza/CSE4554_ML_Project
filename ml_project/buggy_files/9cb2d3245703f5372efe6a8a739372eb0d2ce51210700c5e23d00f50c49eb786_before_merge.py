    def get_chassis_power(self):
        result = {}
        key = "Power"

        # Get these entries, but does not fail if not found
        properties = ['Name', 'PowerAllocatedWatts',
                      'PowerAvailableWatts', 'PowerCapacityWatts',
                      'PowerConsumedWatts', 'PowerMetrics',
                      'PowerRequestedWatts', 'RelatedItem', 'Status']

        chassis_power_results = []
        # Go through list
        for chassis_uri in self.chassis_uri_list:
            chassis_power_result = {}
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            if key in data:
                response = self.get_request(self.root_uri + chassis_uri +
                                            "/" + key)
                data = response['data']
                if 'PowerControl' in data:
                    if len(data['PowerControl']) > 0:
                        data = data['PowerControl'][0]
                        for property in properties:
                            if property in data:
                                chassis_power_result[property] = data[property]
                else:
                    return {'ret': False, 'msg': 'Key PowerControl not found.'}
                chassis_power_results.append(chassis_power_result)
            else:
                return {'ret': False, 'msg': 'Key Power not found.'}

        result['entries'] = chassis_power_results
        return result