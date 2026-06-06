"""Compatibility wrapper for the old DeepSeek-specific entrypoint.

Prefer:

    python -m daily_admin_benchmark.run_model --provider deepseek ...
"""

from __future__ import annotations

from daily_admin_benchmark.run_model import main


if __name__ == "__main__":
    main()
