import re


def camel_to_snake(name: str) -> str:
    # Insert underscores before any uppercase letter followed by lowercase letters, then convert all to lowercase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def plural(name: str) -> str:
    return f"{name}s"
