from daily_admin_benchmark.model_adapters import OpenAICompatibleLLM
from daily_admin_benchmark.run_deepseek import main as legacy_deepseek_main
from daily_admin_benchmark.run_model import (
    PROVIDERS,
    SUPPORTED_ATTACKS,
    _resolve_models,
    main as generic_main,
    summarize_results,
)


def test_model_runner_has_openai_compatible_provider_presets():
    assert {
        "deepseek",
        "siliconflow",
        "openai",
        "openrouter",
        "together",
        "groq",
        "fireworks",
        "local",
        "custom",
    }.issubset(PROVIDERS)
    assert PROVIDERS["deepseek"].default_model == "deepseek-v4-flash"
    assert PROVIDERS["siliconflow"].default_base_url == "https://api.siliconflow.cn/v1"
    assert PROVIDERS["siliconflow"].model_env == "SILICONFLOW_MODEL"
    assert PROVIDERS["siliconflow"].model_list_env == "SILICONFLOW_MODELS"
    assert PROVIDERS["custom"].default_base_url is None


def test_model_runner_resolves_siliconflow_model_list_env(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_MODEL", "single/model")
    monkeypatch.setenv("SILICONFLOW_MODELS", "model/a, model/b,,\nmodel/c")

    assert _resolve_models(PROVIDERS["siliconflow"], None) == ("model/a", "model/b", "model/c")
    assert _resolve_models(PROVIDERS["siliconflow"], "override/model") == ("override/model",)


def test_model_runner_falls_back_to_single_model_env(monkeypatch):
    monkeypatch.delenv("SILICONFLOW_MODELS", raising=False)
    monkeypatch.setenv("SILICONFLOW_MODEL", "single/model")

    assert _resolve_models(PROVIDERS["siliconflow"], None) == ("single/model",)


def test_deepseek_entrypoint_is_legacy_wrapper():
    assert legacy_deepseek_main is generic_main


def test_model_runner_lists_supported_attack_styles():
    assert {
        "tool_knowledge",
        "embedded_procedure",
        "procedure_update",
        "metadata_instruction",
        "delayed_action",
        "cross_tool",
    } == set(SUPPORTED_ATTACKS)


def test_result_summary_tracks_utility_attack_success_overlap():
    results = {
        "utility_results": {
            ("user_task_0", "injection_task_0"): True,
            ("user_task_0", "injection_task_1"): True,
            ("user_task_1", "injection_task_0"): False,
            ("user_task_1", "injection_task_1"): False,
        },
        "security_results": {
            ("user_task_0", "injection_task_0"): True,
            ("user_task_0", "injection_task_1"): False,
            ("user_task_1", "injection_task_0"): True,
            ("user_task_1", "injection_task_1"): False,
        },
    }

    summary = summarize_results(results)

    assert summary["total_pairs"] == 4
    assert summary["utility_passed"] == 2
    assert summary["injection_successes"] == 2
    assert summary["utility_and_injection_successes"] == 1
    assert summary["utility_rate"] == 0.5
    assert summary["injection_success_rate"] == 0.5
    assert summary["utility_and_injection_success_rate"] == 0.25


def test_openai_compatible_llm_forwards_max_tokens():
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return None

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    llm = OpenAICompatibleLLM(client=FakeClient(), model="provider/model", max_tokens=1024)

    assert llm._completion([], []) is None
    assert calls[0]["max_tokens"] == 1024
