async def train_core(
    domain_file: Text = "domain.yml",
    model_directory: Text = "models",
    model_name: Text = "current",
    training_data_file: Text = "data/stories.md",
):
    agent = Agent(
        domain_file,
        policies=[
            MemoizationPolicy(max_history=3),
            MappingPolicy(),
            RestaurantPolicy(batch_size=100, epochs=100, validation_split=0.2),
        ],
    )

    training_data = await agent.load_data(training_data_file, augmentation_factor=10)
    agent.train(training_data)

    # Attention: agent.persist stores the model and all meta data into a folder.
    # The folder itself is not zipped.
    model_path = os.path.join(model_directory, model_name, "core")
    agent.persist(model_path)

    logger.info("Model trained. Stored in '{}'.".format(model_path))

    return model_path