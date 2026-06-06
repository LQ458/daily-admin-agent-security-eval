"""Lightweight imports for AgentDojo classes used by this custom suite.

AgentDojo's public `agentdojo.task_suite` package eagerly imports the default
suites. In some local scientific Python environments that can pull in heavy
native Pandas/PyArrow modules before a custom suite is even loaded. This module
loads the `TaskSuite` implementation directly while still using AgentDojo's
real base task and runtime classes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import agentdojo


def _load_task_suite_class():
    task_suite_path = Path(agentdojo.__file__).parent / "task_suite" / "task_suite.py"
    spec = importlib.util.spec_from_file_location("_daily_admin_agentdojo_task_suite", task_suite_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load AgentDojo TaskSuite from {task_suite_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TaskSuite


TaskSuite = _load_task_suite_class()
