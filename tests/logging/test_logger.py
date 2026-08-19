import json

from service_kit.logging import configure_logger, logger


def _capture_log_record(**extra_fields) -> dict:
    captured = []
    handler_id = logger.add(
        lambda message: captured.append(str(message)),
        format="{extra[serialized]}",
        level=0,
    )
    try:
        logger.info("test", **extra_fields)
    finally:
        logger.remove(handler_id)
    return json.loads(captured[0])


def test_sort_fields_sorts_keys_alphabetically():
    configure_logger(log_level=50000, log_directory=None, pretty_print_logs=False, sort_fields=True)

    data = _capture_log_record(zebra=1, apple=2)

    assert list(data.keys()) == sorted(data.keys())


def test_sort_fields_disabled_preserves_insertion_order():
    configure_logger(
        log_level=50000, log_directory=None, pretty_print_logs=False, sort_fields=False
    )

    data = _capture_log_record(zebra=1, apple=2)
    keys = list(data.keys())

    assert keys.index("zebra") < keys.index("apple")
    assert list(keys) != sorted(keys)


def test_configure_extra():
    extra = {"extra_1": 42, "extra2": "6-7!!!"}
    configure_logger(log_level=5000, log_directory=None, pretty_print_logs=False, extra=extra)

    data = _capture_log_record(zebra=1, apple=2)

    # Verifies all extras are included in the log
    intersection = {k: data[k] for k in data.keys() & extra.keys()}
    assert intersection == extra
