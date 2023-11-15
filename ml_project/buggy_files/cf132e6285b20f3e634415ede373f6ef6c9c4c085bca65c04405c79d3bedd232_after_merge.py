def mock_storage_client():
    """Mocks storage client that treats a local dir as durable storage."""
    client = get_sync_client(LOCAL_SYNC_TEMPLATE, LOCAL_DELETE_TEMPLATE)
    path = os.path.join(ray.utils.get_user_temp_dir(),
                        f"mock-client-{uuid.uuid4().hex[:4]}")
    os.makedirs(path, exist_ok=True)
    client.set_logdir(path)
    return client