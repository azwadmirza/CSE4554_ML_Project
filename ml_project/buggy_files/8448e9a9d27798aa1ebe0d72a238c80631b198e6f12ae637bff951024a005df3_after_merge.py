def try_import_tf(error=False):
    """Tries importing tf and returns the module (or None).

    Args:
        error (bool): Whether to raise an error if tf cannot be imported.

    Returns:
        Tuple:
            - tf1.x module (either from tf2.x.compat.v1 OR as tf1.x).
            - tf module (resulting from `import tensorflow`).
                Either tf1.x or 2.x.
            - The actually installed tf version as int: 1 or 2.

    Raises:
        ImportError: If error=True and tf is not installed.
    """
    # Make sure, these are reset after each test case
    # that uses them: del os.environ["RLLIB_TEST_NO_TF_IMPORT"]
    if "RLLIB_TEST_NO_TF_IMPORT" in os.environ:
        logger.warning("Not importing TensorFlow for test purposes")
        return None, None, None

    if "TF_CPP_MIN_LOG_LEVEL" not in os.environ:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Try to reuse already imported tf module. This will avoid going through
    # the initial import steps below and thereby switching off v2_behavior
    # (switching off v2 behavior twice breaks all-framework tests for eager).
    was_imported = False
    if "tensorflow" in sys.modules:
        tf_module = sys.modules["tensorflow"]
        was_imported = True

    else:
        try:
            import tensorflow as tf_module
        except ImportError as e:
            if error:
                raise e
            return None, None, None

    # Try "reducing" tf to tf.compat.v1.
    try:
        tf1_module = tf_module.compat.v1
        if not was_imported:
            tf1_module.disable_v2_behavior()
            tf1_module.enable_resource_variables()
    # No compat.v1 -> return tf as is.
    except AttributeError:
        tf1_module = tf_module

    if not hasattr(tf_module, "__version__"):
        version = 1  # sphinx doc gen
    else:
        version = 2 if "2." in tf_module.__version__[:2] else 1

    return tf1_module, tf_module, version