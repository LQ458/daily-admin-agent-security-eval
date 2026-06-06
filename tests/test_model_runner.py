from daily_admin_benchmark.run_deepseek import main as legacy_deepseek_main
from daily_admin_benchmark.run_model import PROVIDERS, main as generic_main


def test_model_runner_has_openai_compatible_provider_presets():
    assert {
        "deepseek",
        "openai",
        "openrouter",
        "together",
        "groq",
        "fireworks",
        "local",
        "custom",
    }.issubset(PROVIDERS)
    assert PROVIDERS["deepseek"].default_model == "deepseek-v4-flash"
    assert PROVIDERS["custom"].default_base_url is None


def test_deepseek_entrypoint_is_legacy_wrapper():
    assert legacy_deepseek_main is generic_main
