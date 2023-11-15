		def to_ipnetwork(address):
			prefix = address["netmask"]
			if "/" in prefix:
				# v6 notation in netifaces output, e.g. "ffff:ffff:ffff:ffff::/64"
				_, prefix = prefix.split("/")

			addr = address["addr"]
			if "%" in addr:
				# interface comment in netifaces output, e.g. "fe80::457f:bbee:d579:1063%wlan0"
				addr = addr[:addr.find("%")]
			return netaddr.IPNetwork("{}/{}".format(addr, prefix))