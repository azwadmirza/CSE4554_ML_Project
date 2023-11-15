    def get_fan_inventory(self):
        result = {}
        fan_details = []
        key = "Thermal"

        # Go through list
        for chassis_uri in self.chassis_uri_list:
            response = self.get_request(self.root_uri + chassis_uri)
            if response['ret'] is False:
                return response
            result['ret'] = True
            data = response['data']
            if key in data:
                # match: found an entry for "Thermal" information = fans
                thermal_uri = data[key]["@odata.id"]
                response = self.get_request(self.root_uri + thermal_uri)
                if response['ret'] is False:
                    return response
                result['ret'] = True
                data = response['data']

                for device in data[u'Fans']:
                    fan_details.append(dict(
                        # There is more information available but this is most important
                        Name=device[u'FanName'],
                        RPMs=device[u'Reading'],
                        State=device[u'Status'][u'State'],
                        Health=device[u'Status'][u'Health']))
                result["entries"] = fan_details
        return result