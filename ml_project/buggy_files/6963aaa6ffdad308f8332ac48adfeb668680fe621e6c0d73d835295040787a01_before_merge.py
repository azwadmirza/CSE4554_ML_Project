def ParseDNS(dns_packet_data):
  """Parse DNS packets and return a string with relevant details.

  Args:
    dns_packet_data: DNS packet data.

  Returns:
    Formatted DNS details.
  """
  dns_data = []

  try:
    dns = dpkt.dns.DNS(dns_packet_data)
    if dns.rcode is dpkt.dns.DNS_RCODE_NOERR:
      if dns.get_qr() == 1:
        if not dns.an:
          dns_data.append(u'DNS Response: No answer for ')
          dns_data.append(dns.qd[0].name)
        else:
          # Type of DNS answer.
          for answer in dns.an:
            if answer.type == 5:
              dns_data.append(u'DNS-CNAME request ')
              dns_data.append(answer.name)
              dns_data.append(u' response: ')
              dns_data.append(answer.cname)
            elif answer.type == 1:
              dns_data.append(u'DNS-A request ')
              dns_data.append(answer.name)
              dns_data.append(u' response: ')
              dns_data.append(socket.inet_ntoa(answer.rdata))
            elif answer.type == 12:
              dns_data.append(u'DNS-PTR request ')
              dns_data.append(answer.name)
              dns_data.append(u' response: ')
              dns_data.append(answer.ptrname)
      elif not dns.get_qr():
        dns_data.append(u'DNS Query for ')
        dns_data.append(dns.qd[0].name)
    else:
      dns_data.append(u'DNS error code ')
      dns_data.append(str(dns.rcode))

  except dpkt.UnpackError as exception:
    dns_data.append(u'DNS Unpack Error: {0:s}. First 20 of data {1:s}'.format(
        exception, repr(dns_packet_data[:20])))
  except IndexError as exception:
    dns_data.append(u'DNS Index Error: {0:s}'.format(exception))

  return u' '.join(dns_data)