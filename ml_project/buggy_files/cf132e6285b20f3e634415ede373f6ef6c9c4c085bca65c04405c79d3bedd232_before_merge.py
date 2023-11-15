def mock_storage_client():
    """Mocks storage client that treats a local dir as durable storage."""
    return get_sync_client(LOCAL_SYNC_TEMPLATE, LOCAL_DELETE_TEMPLATE)