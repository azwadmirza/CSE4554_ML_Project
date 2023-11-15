def main():
    from ..exceptions import conda_exception_handler
    return conda_exception_handler(_main)