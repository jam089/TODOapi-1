import re


def camel_to_snake(input_line: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", input_line).lower()
