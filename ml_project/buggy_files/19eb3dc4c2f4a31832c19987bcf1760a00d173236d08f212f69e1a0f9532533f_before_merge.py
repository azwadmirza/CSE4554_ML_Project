async def edit_instance():
    _instance_list = load_existing_config()
    if not _instance_list:
        print("No instances have been set up!")
        return

    print(
        "You have chosen to edit an instance. The following "
        "is a list of instances that currently exist:\n"
    )
    for instance in _instance_list.keys():
        print("{}\n".format(instance))
    print("Please select one of the above by entering its name")
    selected = input("> ")

    if selected not in _instance_list.keys():
        print("That isn't a valid instance!")
        return
    _instance_data = _instance_list[selected]
    default_dirs = deepcopy(data_manager.basic_config_default)

    current_data_dir = Path(_instance_data["DATA_PATH"])
    print("You have selected '{}' as the instance to modify.".format(selected))
    if not confirm("Please confirm (y/n):"):
        print("Ok, we will not continue then.")
        return

    print("Ok, we will continue on.")
    print()
    if confirm("Would you like to change the instance name? (y/n)"):
        name = get_name()
    else:
        name = selected

    if confirm("Would you like to change the data location? (y/n)"):
        default_data_dir = get_data_dir()
        default_dirs["DATA_PATH"] = str(default_data_dir.resolve())
    else:
        default_dirs["DATA_PATH"] = str(current_data_dir.resolve())

    if name != selected:
        save_config(selected, {}, remove=True)
    save_config(name, default_dirs)

    print("Your basic configuration has been edited")