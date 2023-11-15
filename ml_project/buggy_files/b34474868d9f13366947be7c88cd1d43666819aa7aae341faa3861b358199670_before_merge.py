def resource(service_name: str, session: Optional[boto3.Session] = None) -> boto3.resource:
    """Create a valid boto3.resource."""
    return ensure_session(session=session).resource(
        service_name=service_name,
        use_ssl=True,
        config=botocore.config.Config(
            retries={"max_attempts": 10, "mode": "adaptive"}, connect_timeout=10, max_pool_connections=30
        ),
    )