---
trigger: always_on
description: Python development guidelines
---

## Set up environment

Always set up a Python virtual environment and install dependencies from `requirements.txt` before running Python scripts.
You can do this by running:
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`

## Guidelines

- every time we install and use a new dependency, we must add it to `requirements.txt` (we can use `pip freeze` to update it?)
- every time we create a new Python script, we should create its test in `scripts/tests` folder
- every time we update a Python script, we should run all tests and update test(s) properly if needed