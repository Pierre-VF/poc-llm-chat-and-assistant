import ast

from pydantic import BaseModel


class PythonFileTopLevelElements(BaseModel):
    """This is a class that contains key elements for LLM to augment and/or address"""

    imports: list[str] = []
    functions: list[str] = []
    classes: list[str] = []
    __other: list[str] = []


def split_python_file(file_path: str) -> PythonFileTopLevelElements:
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    imports = []
    functions = []
    classes = []
    other = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.FunctionDef):
            functions.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.ClassDef):
            classes.append(ast.get_source_segment(source, node))

    return PythonFileTopLevelElements(
        **{
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "other": other,
        }
    )


if __name__ == "__main__":
    from pathlib import Path

    x = Path(__file__).parent.parent / "config.py"
    out = split_python_file(str(x))

    with open("updated.json", "w") as f:
        f.write(out.model_dump_json(indent=4))

    print("DONE")
