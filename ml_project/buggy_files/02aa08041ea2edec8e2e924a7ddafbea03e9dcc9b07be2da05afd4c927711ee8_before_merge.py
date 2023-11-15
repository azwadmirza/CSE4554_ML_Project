def load_ecr_image_scan_findings(neo4j_session, data, aws_update_tag):
    """
    Creates the path (:Risk:CVE:ECRScanFinding)-[:AFFECTS]->(:Package)-[:DEPLOYED]->(:ECRImage)
    :param neo4j_session: The Neo4j session object
    :param data: A dict that has been run through transform_ecr_scan_finding_attributes().
    :param aws_update_tag: The AWS update tag
    """
    query = """
    UNWIND {Risks} as risk
        MATCH (image:ECRImage{id: {ImageDigest}})
        MERGE (pkg:Package{id: risk.package_version + "|" + risk.package_name})
        ON CREATE SET pkg.firstseen = timestamp(),
        pkg.name = risk.package_name,
        pkg.version = risk.package_version
        SET pkg.lastupdated = {aws_update_tag}
        WITH image, risk, pkg

        MERGE (pkg)-[r1:DEPLOYED]->(image)
        ON CREATE SET r1.firstseen = timestamp()
        SET r1.lastupdated = {aws_update_tag}
        WITH pkg, risk

        MERGE (r:Risk:CVE:ECRScanFinding{id: risk.name})
        ON CREATE SET r.firstseen = timestamp(),
        r.name = risk.name,
        r.severity = risk.severity
        SET r.lastupdated = {aws_update_tag},
        r.uri = risk.uri,
        r.cvss2_score = risk.CVSS2_SCORE

        MERGE (r)-[a:AFFECTS]->(pkg)
        ON CREATE SET a.firstseen = timestamp()
        SET r.lastupdated = {aws_update_tag}
        """
    neo4j_session.run(
        query,
        Risks=data['findings'],
        ImageDigest=data['imageDigest'],
        aws_update_tag=aws_update_tag,
    )