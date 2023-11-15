def create_token(name, scope):
    """
    Create a Prefect Cloud API token.

    For more info on API tokens visit https://docs.prefect.io/orchestration/concepts/api.html

    \b
    Options:
        --name, -n      TEXT    A name to give the generated token
        --scope, -r     TEXT    A scope for the token
    """
    check_override_auth_token()

    client = Client()

    output = client.graphql(
        query={
            "mutation($input: create_api_token_input!)": {
                "create_api_token(input: $input)": {"token"}
            }
        },
        variables=dict(input=dict(name=name, scope=scope)),
    )

    if not output.get("data", None):
        click.secho("Issue creating API token", fg="red")
        return

    click.echo(output.data.create_api_token.token)