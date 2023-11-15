def sync_gcp_subnets(neo4j_session, compute, project_id, regions, gcp_update_tag, common_job_parameters):
    for r in regions:
        subnet_res = get_gcp_subnets(project_id, r, compute)
        subnets = transform_gcp_subnets(subnet_res)
        load_gcp_subnets(neo4j_session, subnets, gcp_update_tag)
        # TODO scope the cleanup to the current project - https://github.com/lyft/cartography/issues/381
        cleanup_gcp_subnets(neo4j_session, common_job_parameters)