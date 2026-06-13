"""Helper for VigiEau."""

from typing import Any

JSONType = dict[str, Any] | list[Any]


def find_item(data: dict[str, Any], key_chain: str, default: Any = None) -> Any:
    """Get recursive key and return value.

    Parameters:
        data (dict[str, Any]) : dictionary to search
        key (str): searched string with dot for key delimited (ex: "key.key.key")
            It is possible to integrate an element of an array by indicating its index number
        default (Any): default value to return if key not found
    Returns:
        Any: value of the key or default if not found
    Example:
        >>> find_item({"a": {"b": [{"c": "value_a"},{"d": "value_b"}]}}, "a.b.0.c")
        "value_a"
        >>> find_item({"a": {"b": [{"c": "value"}]}}, "a.b.1.c", "default")
        "default"
    """
    for key in key_chain.split("."):
        if isinstance(data, dict):
            data = data.get(key)
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return default
        if data is None:
            break
    return data if data is not None else default


def find_root_item(
    data: list[dict[str, Any]], key: str, value: Any, default: Any = None
) -> Any | None:
    """Search recursively in a list of nested dictionaries.

    Parameters:
        data (list[dict[str, Any]]): list of dictionaries to search
        key (str): key to search for
        value (Any): value to match against the key
        default (Any): default value to return if no match is found

    Returns:
        Any | None: the first matching item or default if not found

    Example:
        >>> find_root_item([{"a": 1}, {"b": 2, "d":4}, {"c": 3}], "b", 2)
        {"b": 2, "d":4}
        >>> find_root_item([{"a": 1}, {"b": 2}, {"c": 3}], "d", 4, default="not found")
        "not found

    """
    if not data:
        return default
    for item in data:
        if contains_key_value(item, key, value):
            return item
    return default


def contains_key_value(data: JSONType, key: str, value: Any) -> bool:
    """Search recursively for key == value in a dictionary or list."""
    if isinstance(data, dict):
        if data.get(key) == value:
            return True
        return any(contains_key_value(v, key, value) for v in data.values())
    if isinstance(data, list):
        return any(contains_key_value(i, key, value) for i in data)
    return False
