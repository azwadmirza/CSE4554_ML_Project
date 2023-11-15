def _attach_firewall_rules(neo4j_session, fw, gcp_update_tag):
    """
    Attach the allow_rules to the Firewall object
    :param neo4j_session: The Neo4j session
    :param fw: The Firewall object
    :param gcp_update_tag: The timestamp
    :return: Nothing
    """
    template = Template("""
    MATCH (fw:GCPFirewall{id:{FwPartialUri}})

    MERGE (rule:IpRule:IpPermissionInbound:GCPIpRule{id:{RuleId}})
    ON CREATE SET rule.firstseen = timestamp(),
    rule.ruleid = {RuleId}
    SET rule.protocol = {Protocol},
    rule.fromport = {FromPort},
    rule.toport = {ToPort},
    rule.lastupdated = {gcp_update_tag}

    MERGE (rng:IpRange{id:{Range}})
    ON CREATE SET rng.firstseen = timestamp(),
    rng.range = {Range}
    SET rng.lastupdated = {gcp_update_tag}

    MERGE (rng)-[m:MEMBER_OF_IP_RULE]->(rule)
    ON CREATE SET m.firstseen = timestamp()
    SET m.lastupdated = {gcp_update_tag}

    MERGE (fw)<-[r:$fw_rule_relationship_label]-(rule)
    ON CREATE SET r.firstseen = timestamp()
    SET r.lastupdated = {gcp_update_tag}
    """)
    for list_type in 'transformed_allow_list', 'transformed_deny_list':
        if list_type == 'transformed_allow_list':
            label = "ALLOWED_BY"
        else:
            label = "DENIED_BY"
        for rule in fw[list_type]:
            # It is possible for sourceRanges to not be specified for this rule
            # If sourceRanges is not specified then the rule must specify sourceTags.
            # Since an IP range cannot have a tag applied to it, it is ok if we don't ingest this rule.
            for ip_range in fw.get('sourceRanges', []):
                neo4j_session.run(
                    template.safe_substitute(fw_rule_relationship_label=label),
                    FwPartialUri=fw['id'],
                    RuleId=rule['ruleid'],
                    Protocol=rule['protocol'],
                    FromPort=rule.get('fromport'),
                    ToPort=rule.get('toport'),
                    Range=ip_range,
                    gcp_update_tag=gcp_update_tag,
                )