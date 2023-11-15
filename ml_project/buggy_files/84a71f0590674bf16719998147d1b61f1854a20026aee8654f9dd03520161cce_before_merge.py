def get_domain_mx_list(domain):
    """Return a list of MX IP address for domain."""
    result = []
    logger = logging.getLogger("modoboa.admin")
    dns_server = param_tools.get_global_parameter("custom_dns_server")
    if dns_server:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
    else:
        resolver = dns.resolver

    try:
        dns_answers = resolver.query(domain, "MX")
    except dns.resolver.NXDOMAIN as e:
        logger.error(_("No DNS records found for %s") % domain, exc_info=e)
    except dns.resolver.NoAnswer as e:
        logger.error(_("No MX record for %s") % domain, exc_info=e)
    except dns.resolver.NoNameservers as e:
        logger.error(_("No working name servers found"), exc_info=e)
    except dns.resolver.Timeout as e:
        logger.warning(
            _("DNS resolution timeout, unable to query %s at the moment") %
            domain, exc_info=e)
    else:
        for dns_answer in dns_answers:
            for rtype in ["A", "AAAA"]:
                try:
                    mx_domain = dns_answer.exchange.to_unicode(
                        omit_final_dot=True, idna_codec=IDNA_2008_UTS_46)
                    ip_answers = resolver.query(mx_domain, rtype)
                except dns.resolver.NXDOMAIN as e:
                    logger.error(
                        _("No {type} record found for MX {mx}").format(
                            type=rtype, mx=domain), exc_info=e)
                else:
                    for ip_answer in ip_answers:
                        try:
                            address_smart = smart_text(ip_answer.address)
                            mx_ip = ipaddress.ip_address(address_smart)
                        except ValueError as e:
                            logger.warning(
                                _("Invalid IP address format for "
                                  "{domain}; {addr}").format(
                                      domain=mx_domain,
                                      addr=smart_text(ip_answer.address)
                                  ), exc_info=e)
                        else:
                            result.append((mx_domain, mx_ip))
    return result