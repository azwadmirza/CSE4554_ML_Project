def client(service_name: str, session: Optional[boto3.Session] = None) -> boto3.client:
    """Create a valid boto3.client."""
    return ensure_session(session=session).client(
        service_name=service_name,
        use_ssl=True,
        config=botocore.config.Config(retries={"max_attempts": 5}, connect_timeout=10, max_pool_connections=10),
    )