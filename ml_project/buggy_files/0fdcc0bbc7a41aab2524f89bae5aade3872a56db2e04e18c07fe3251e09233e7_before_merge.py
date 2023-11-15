    def query(ip):
        raw_result = Cymru.__ip_query(ip)
        results = map(Cymru.__ip_query_parse, raw_result)
        result = None
        for res in results:
            if result is None:
                result = res
            elif 'network' not in res:
                continue
            elif 'network' not in result:
                result = res
            else:
                ips_a = ipaddress.ip_network(res['network']).num_addresses
                ips_b = ipaddress.ip_network(result['network']).num_addresses
                if ips_a < ips_b:
                    result = res

        if "asn" in result:
            raw_result = Cymru.__asn_query(result['asn'])
            extra_info = Cymru.__asn_query_parse(raw_result)
            result.update(extra_info)

        return result