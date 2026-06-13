import csv
import subprocess
import sys

from daily_admin_benchmark.resume_missing import (
    build_report_command,
    build_resume_argvs,
    build_resume_commands,
    execute_resume_commands,
    load_missing_pairs,
)


def test_load_missing_pairs_groups_and_sorts_injection_tasks(tmp_path):
    path = tmp_path / "missing.csv"
    rows = [
        {
            "model": "model/b",
            "pipeline_name": "pipeline-b",
            "run_type": "paired",
            "user_task": "user_task_0",
            "injection_task": "injection_task_10",
        },
        {
            "model": "model/b",
            "pipeline_name": "pipeline-b",
            "run_type": "paired",
            "user_task": "user_task_0",
            "injection_task": "injection_task_2",
        },
        {
            "model": "model/a",
            "pipeline_name": "pipeline-a",
            "run_type": "standalone",
            "user_task": "",
            "injection_task": "injection_task_1",
        },
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    assert load_missing_pairs(path) == {("model/b", "user_task_0"): ["injection_task_2", "injection_task_10"]}


def test_build_resume_commands_quotes_model_ids():
    commands = build_resume_commands(
        missing_pairs={("provider/model", "user_task_0"): ["injection_task_1", "injection_task_2"]},
        provider="siliconflow",
        attack="cross_tool",
        api_timeout=45,
    )

    assert commands == [
        "python -m daily_admin_benchmark.run_model --provider siliconflow --model provider/model "
        "--attack cross_tool --user-task user_task_0 --api-timeout 45 "
        "--injection-task injection_task_1 --injection-task injection_task_2"
    ]


def test_build_resume_commands_can_chunk_injection_tasks():
    commands = build_resume_commands(
        missing_pairs={("provider/model", "user_task_0"): ["injection_task_1", "injection_task_2", "injection_task_3"]},
        provider="siliconflow",
        attack="cross_tool",
        api_timeout=45,
        chunk_size=2,
    )

    assert len(commands) == 2
    assert "--injection-task injection_task_1 --injection-task injection_task_2" in commands[0]
    assert "--injection-task injection_task_3" in commands[1]


def test_build_resume_argvs_uses_current_python_executable():
    argvs = build_resume_argvs(
        missing_pairs={("provider/model", "user_task_0"): ["injection_task_1"]},
        provider="siliconflow",
        attack="cross_tool",
        api_timeout=45,
    )

    assert argvs[0][:3] == [sys.executable, "-m", "daily_admin_benchmark.run_model"]
    assert "--model" in argvs[0]
    assert "provider/model" in argvs[0]


def test_build_resume_argvs_can_forward_max_tokens():
    argvs = build_resume_argvs(
        missing_pairs={("provider/model", "user_task_0"): ["injection_task_1"]},
        provider="siliconflow",
        attack="cross_tool",
        api_timeout=45,
        max_tokens=512,
    )

    assert "--max-tokens" in argvs[0]
    assert "512" in argvs[0]


def test_execute_resume_commands_stops_on_first_failure(monkeypatch):
    calls = []

    def fake_run(argv):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, returncode=3)

    monkeypatch.setattr(subprocess, "run", fake_run)

    status = execute_resume_commands([["cmd-1"], ["cmd-2"]])

    assert status == 3
    assert calls == [["cmd-1"]]


def test_execute_resume_commands_sleeps_between_successful_commands(monkeypatch):
    calls = []
    sleeps = []

    def fake_run(argv):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr("daily_admin_benchmark.resume_missing.time.sleep", sleeps.append)

    status = execute_resume_commands([["cmd-1"], ["cmd-2"]], sleep_between=2.5)

    assert status == 0
    assert calls == [["cmd-1"], ["cmd-2"]]
    assert sleeps == [2.5]


def test_execute_resume_commands_retries_failed_command(monkeypatch):
    calls = []
    sleeps = []

    def fake_run(argv):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, returncode=1 if len(calls) == 1 else 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr("daily_admin_benchmark.resume_missing.time.sleep", sleeps.append)

    status = execute_resume_commands([["cmd-1"]], retries=1, retry_sleep=4)

    assert status == 0
    assert calls == [["cmd-1"], ["cmd-1"]]
    assert sleeps == [4]


def test_build_report_command_points_to_report_module(tmp_path):
    argv = build_report_command(
        provider="siliconflow",
        attack="cross_tool",
        outdir=tmp_path / "out",
        user_task_count=1,
        injection_task_count=50,
    )

    assert argv[:3] == [sys.executable, "-m", "daily_admin_benchmark.report_results"]
    assert "--outdir" in argv
    assert str(tmp_path / "out") in argv
