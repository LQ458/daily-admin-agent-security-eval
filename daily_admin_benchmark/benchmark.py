"""Register the custom AgentDojo suite.

AgentDojo scripts load this module with `-ml daily_admin_benchmark.benchmark`.
"""

from agentdojo.task_suite.load_suites import register_suite

from daily_admin_benchmark.suites.daily_admin import task_suite


BENCHMARK_VERSION = "daily_admin_mini"

register_suite(task_suite, BENCHMARK_VERSION)
