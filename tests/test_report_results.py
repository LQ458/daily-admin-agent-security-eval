import json

from daily_admin_benchmark.report_results import (
    ModelSummary,
    PairResult,
    collect_results,
    write_csv,
    write_injection_charts,
    write_statistical_analysis,
    write_task_risk_files,
)


def test_collect_results_ignores_incomplete_trace_logs(tmp_path):
    log_path = (
        tmp_path
        / "siliconflow-model"
        / "daily_admin"
        / "user_task_0"
        / "cross_tool"
        / "injection_task_0.json"
    )
    log_path.parent.mkdir(parents=True)
    log_path.write_text(json.dumps({"duration": 0.1, "error": None}))

    pairs, standalone, missing_pairs, missing_standalone, summaries = collect_results(
        models=("model",),
        logdir=tmp_path,
        provider="siliconflow",
        attack="cross_tool",
        user_tasks=("user_task_0",),
        injection_tasks=("injection_task_0",),
    )

    assert pairs == []
    assert standalone == []
    assert len(missing_pairs) == 1
    assert len(missing_standalone) == 1
    assert summaries[0].completed_pairs == 0


def test_write_csv_outputs_attackability_rank(tmp_path):
    summaries = [
        ModelSummary(
            model="safer-model",
            pipeline_name="safer-model",
            expected_pairs=2,
            completed_pairs=2,
            utility_passed=2,
            attack_successes=0,
            utility_and_attack=0,
            safe_utility=2,
            standalone_expected=2,
            standalone_completed=2,
            standalone_passed=2,
            errors=0,
            total_duration=1.0,
        ),
        ModelSummary(
            model="easier-attack-model",
            pipeline_name="easier-attack-model",
            expected_pairs=2,
            completed_pairs=2,
            utility_passed=2,
            attack_successes=2,
            utility_and_attack=2,
            safe_utility=0,
            standalone_expected=2,
            standalone_completed=2,
            standalone_passed=2,
            errors=0,
            total_duration=1.0,
        ),
    ]

    write_csv([], [], [], [], summaries, tmp_path)

    attackability_rank = (tmp_path / "attackability_rank.csv").read_text().splitlines()
    coverage_status = (tmp_path / "coverage_status.csv").read_text().splitlines()
    model_summary = (tmp_path / "model_summary.csv").read_text()

    assert attackability_rank[0].startswith("attackability_rank,model")
    assert attackability_rank[1].split(",")[:2] == ["1", "easier-attack-model"]
    assert coverage_status[0].startswith("model,completed_pairs,expected_pairs")
    assert "complete" in coverage_status[1]
    assert "attackability_rank" in model_summary.splitlines()[0]


def test_analysis_outputs_include_task_risk_map(tmp_path):
    summary = ModelSummary(
        model="model",
        pipeline_name="model",
        expected_pairs=1,
        completed_pairs=1,
        utility_passed=1,
        attack_successes=1,
        utility_and_attack=1,
        safe_utility=0,
        standalone_expected=1,
        standalone_completed=1,
        standalone_passed=1,
        errors=0,
        total_duration=1.0,
    )
    pair = PairResult(
        model="model",
        pipeline_name="model",
        user_task="user_task_0",
        injection_task="injection_task_0",
        utility=True,
        attack_success=True,
        duration=1.0,
        error=None,
    )

    write_task_risk_files(tmp_path, [pair], [summary], ("injection_task_0",))
    write_statistical_analysis(tmp_path, [summary], [pair], "siliconflow", "cross_tool")
    write_injection_charts([pair], [summary], tmp_path)

    assert "Workflow contamination" in (tmp_path / "task_risk_map.md").read_text()
    assert "linked_action" in (tmp_path / "task_risk_map.csv").read_text()
    assert "Overall Rates" in (tmp_path / "statistical_analysis.md").read_text()
    assert (tmp_path / "risk_category_rollup.csv").exists()
    assert (tmp_path / "injection_attack_success.svg").exists()
