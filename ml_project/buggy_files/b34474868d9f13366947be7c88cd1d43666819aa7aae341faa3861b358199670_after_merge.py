def resource(service_name: str, session: Optional[boto3.Session] = None) -> boto3.resource:
    """Create a valid boto3.resource."""
    return ensure_session(session=session).resource(service_name=service_name, use_ssl=True, config=botocore_config())