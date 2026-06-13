from pathlib import Path

import yaml

from daily_admin_benchmark.suites.daily_admin import task_suite


ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "daily_admin_benchmark" / "suites" / "daily_admin"
DATA_DIR = ROOT / "daily_admin_benchmark" / "data" / "suites" / "daily_admin"


def test_suite_has_agentdojo_structure():
    expected = {
        "task_suite.py",
        "tools.py",
        "user_tasks.py",
        "injection_tasks.py",
        "__init__.py",
    }

    assert expected.issubset({path.name for path in SUITE_DIR.iterdir()})
    assert (ROOT / "daily_admin_benchmark" / "benchmark.py").exists()


def test_environment_contains_daily_app_surfaces_and_injection_vectors():
    environment = yaml.safe_load((DATA_DIR / "environment.yaml").read_text())
    vectors = yaml.safe_load((DATA_DIR / "injection_vectors.yaml").read_text())

    workspace = environment["workspace"]
    assert set(vectors) == {
        "injection_notion_orientation",
        "injection_canvas_assignment",
        "injection_sis_course_plan",
        "injection_notion_shift_note",
        "injection_duo_request",
        "injection_vault_context",
    }
    assert "{injection_notion_orientation}" in "\n".join(
        workspace["notion_pages"]["orientation_week_plan"]["blocks"]
    )
    assert (
        "{injection_canvas_assignment}"
        in workspace["canvas_courses"]["CSE247"]["assignments"]["cse247_ps1"]["description"]
    )
    assert "{injection_sis_course_plan}" in workspace["course_plan_notes"]["fall_security_plan"]["content"]
    assert "{injection_notion_shift_note}" in "\n".join(workspace["notion_pages"]["campus_it_shift_note"]["blocks"])
    assert "{injection_duo_request}" in workspace["duo_training_prompts"]["duo_workday_unknown"]["prompt_text"]
    assert "{injection_vault_context}" in workspace["mock_vault_records"]["public_study_archive_policy"]["value"]


def test_task_files_register_five_user_and_fifty_injection_tasks():
    user_tasks = (SUITE_DIR / "user_tasks.py").read_text()
    injection_tasks = (SUITE_DIR / "injection_tasks.py").read_text()

    assert user_tasks.count("@task_suite.register_user_task") == 5
    assert injection_tasks.count("@task_suite.register_injection_task") == 8
    assert len(task_suite.user_tasks) == 5
    assert len(task_suite.injection_tasks) == 50
    assert "UserTask0" in user_tasks
    assert "UserTask4" in user_tasks
    assert "InjectionTask0" in injection_tasks
    assert "InjectionTask7" in injection_tasks
    assert "injection_task_49" in task_suite.injection_tasks


def test_tools_reference_realistic_api_families():
    tools = (SUITE_DIR / "tools.py").read_text()

    for api_family in ["notion_", "todoist_", "canvas_", "sis_", "workday_", "duo_", "mock_", "workspace_"]:
        assert api_family in tools
