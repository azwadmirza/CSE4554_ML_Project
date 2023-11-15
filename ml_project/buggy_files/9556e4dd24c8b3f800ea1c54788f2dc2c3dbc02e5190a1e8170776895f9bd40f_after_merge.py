def _print_list(users):
	click.echo("{} users registered in the system:".format(len(users)))
	for user in sorted(map(lambda x: x.as_dict(), users), key=lambda x: sv(x.get("name"))):
		click.echo("\t{}".format(_user_to_line(user)))