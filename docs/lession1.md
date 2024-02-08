### Lesson 1

- Install Tools
- Create Project
- VS Code Finetuning
  - Code Formatting
  - Linting
  - Debugging


# Install Tools

- Python 3.9 or later \
My suggestion ist to use the latest version posibile.
- [Visual Studio Code](https://code.visualstudio.com/)
  - Plugins:
    - Python (with Pylance & Debugger)
    - Black Formatter
    - Flake8
    - isort
  - Optional Plugins:
    - YAML
    - Tiltfile
    - Kubernetes
    - Docker
    - Markdown Preview
    - Jupyter

- [Poetry](https://python-poetry.org/) \
  using pip (outside virtualenv), pipx or brew (macos)

- [Tilt.dev](https://tilt.dev/)

# Create Project

```sh
mkdir dispo
poetry init
# do not define dependencies

```
See result in `pyproject.toml` file.

# Create WebServer

`poetry add fastapi "uvicorn[standart]"`

With `poetry add` the package will also be installed. Use `poetry install` if the dependencies are already declared.

You must create an README.md file, otherwise poetry install will fail.

Let's start with our first code snippet:

```python
#dispo/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world():
    return {"message": "hello world"}

```
To start the app:
```sh
poetry shell
uvicorn main:app
```

Check `http://localhost:8000`

Swagger/OpenApi is already included, see `http://localhost:8000/docs`.


# VS Code Finetuning

## Virtual Environment
Virtual Environments will be recognized when activated at startup. If you prefer the the .venv inside the project directory, do `poetry config virtualenvs.in-project true`.

## Code Formatting

We do use Black as formatter and isort for sorted import statements.

```json
# >Preferences, Open User Settings(Json)
# settings.json - add following:
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit"
        },
    },
    "isort.args":["--profile", "black"],
```

To fix issues with black vs isort, add this

```toml
# pyproject.toml
[tool.isort]
profile = "black"
```

## Linting

Is done by flake8. I do suggest to use the vs-code plugin for this. The following config will fix the usage with Black. This config could NOT be included in pyproject.toml.

```toml
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203
```

If you will now add a not needed import like `import os` then you should notice:

- Sorting the import statements on save
- A new Issue on Problems View

## Debugging

Go to Run&Debug, get to `create a launch.json` - `Python Debugger` - `FastAPI` - defaults should be ok.

- start the app
- set a breakpoint
- check it

