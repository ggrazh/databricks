# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "2"
# ///
# MAGIC %md Test runner for `pytest`

# COMMAND ----------

!pip install pytest

# COMMAND ----------

# pytest.main runs our tests directly in the notebook environment, providing
# fidelity for Spark and other configuration variables.
#
# A limitation of this approach is that changes to the test will be
# cache by Python's import caching mechanism.
#
# To iterate on tests during development, we clear the cached imports of
# our modules and tests instead of restarting the Python process: a restart
# triggered mid-cell drops the sys.path setup below and makes this cell fail
# intermittently with ModuleNotFoundError.
import os
import sys
import pytest

# Drop cached imports so edits to modules/ or the tests are picked up.
for _name in list(sys.modules):
    if _name == "modules" or _name.startswith("modules.") or _name == "transforms_test":
        del sys.modules[_name]
sys.path_importer_cache.clear()

# Run all tests in the repository root.
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
repo_root = os.path.dirname(os.path.dirname(notebook_path))
os.chdir(f'/Workspace/{repo_root}')
%pwd

# pytest.main() (unlike `python -m pytest`) does not add the cwd to sys.path,
# so the repo root must be added explicitly for `modules` to be importable.
sys.path.insert(0, os.getcwd())

# Skip writing pyc files on a readonly filesystem.
sys.dont_write_bytecode = True

# Disable pytest's assertion rewriting, which also writes __pycache__
# directories next to the test files -- unsupported on /Workspace FUSE.
retcode = pytest.main([".", "-p", "no:cacheprovider", "--assert=plain"])

# Fail the cell execution if we have any test failures.
assert retcode == 0, 'The pytest invocation failed. See the log above for details.'