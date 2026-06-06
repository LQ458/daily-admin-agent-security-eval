"""Daily admin AgentDojo suite."""

from daily_admin_benchmark.suites.daily_admin.task_suite import DailyAdminEnvironment, task_suite

# Import tasks so decorators register them with the suite.
from daily_admin_benchmark.suites.daily_admin import injection_tasks as _injection_tasks  # noqa: F401
from daily_admin_benchmark.suites.daily_admin import user_tasks as _user_tasks  # noqa: F401

__all__ = ["DailyAdminEnvironment", "task_suite"]
