"""TaskSuite definition for the daily admin benchmark."""

from pathlib import Path

from agentdojo.functions_runtime import TaskEnvironment, make_function

from daily_admin_benchmark.agentdojo_compat import TaskSuite
from daily_admin_benchmark.suites.daily_admin.tools import (
    DailyAdminWorkspace,
    canvas_get_assignment,
    canvas_list_assignments,
    canvas_submit_assignment,
    duo_decide_training_prompt,
    duo_list_training_prompts,
    get_user_profile,
    mock_send_external_report,
    mock_vault_read_record,
    notion_append_block_children,
    notion_retrieve_block_children,
    notion_search_pages,
    save_agent_memory,
    sis_remove_course_from_plan,
    sis_read_course_plan_note,
    sis_add_course_to_plan,
    sis_search_courses,
    todoist_add_task,
    todoist_complete_task,
    todoist_list_tasks,
    workday_submit_time_entry,
    workday_update_mock_payout_setting,
    workday_update_time_tracking_setting,
    workspace_add_member,
)


class DailyAdminEnvironment(TaskEnvironment):
    workspace: DailyAdminWorkspace


TOOLS = [
    get_user_profile,
    notion_search_pages,
    notion_retrieve_block_children,
    notion_append_block_children,
    todoist_add_task,
    todoist_complete_task,
    todoist_list_tasks,
    canvas_get_assignment,
    canvas_list_assignments,
    canvas_submit_assignment,
    sis_read_course_plan_note,
    sis_search_courses,
    sis_add_course_to_plan,
    sis_remove_course_from_plan,
    workday_submit_time_entry,
    workday_update_time_tracking_setting,
    workday_update_mock_payout_setting,
    duo_list_training_prompts,
    duo_decide_training_prompt,
    mock_vault_read_record,
    mock_send_external_report,
    workspace_add_member,
    save_agent_memory,
]

DATA_PATH = Path(__file__).parents[2] / "data" / "suites" / "daily_admin"

task_suite = TaskSuite[DailyAdminEnvironment](
    "daily_admin",
    DailyAdminEnvironment,
    [make_function(tool) for tool in TOOLS],
    DATA_PATH,
)
