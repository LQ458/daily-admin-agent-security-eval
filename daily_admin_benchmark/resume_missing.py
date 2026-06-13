"""Print or execute grouped commands for resuming missing model-evaluation runs."""

from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


def _task_sort_key(task_id: str) -> tuple[str, int]:
    prefix, _, suffix = task_id.rpartition("_")
    return (prefix, int(suffix) if suffix.isdigit() else -1)


def load_missing_pairs(path: Path) -> dict[tuple[str, str], list[str]]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("run_type") != "paired":
                continue
            model = row["model"]
            user_task = row["user_task"]
            injection_task = row["injection_task"]
            grouped[(model, user_task)].add(injection_task)

    return {
        key: sorted(injection_tasks, key=_task_sort_key)
        for key, injection_tasks in sorted(grouped.items(), key=lambda item: item[0])
    }


def build_resume_command(
    *,
    provider: str,
    model: str,
    attack: str,
    user_task: str,
    injection_tasks: list[str],
    api_timeout: float,
    max_tokens: int | None = None,
) -> str:
    parts = [
        "python",
        "-m",
        "daily_admin_benchmark.run_model",
        "--provider",
        provider,
        "--model",
        model,
        "--attack",
        attack,
        "--user-task",
        user_task,
        "--api-timeout",
        str(api_timeout),
    ]
    if max_tokens is not None:
        parts.extend(["--max-tokens", str(max_tokens)])
    for injection_task in injection_tasks:
        parts.extend(["--injection-task", injection_task])
    return " ".join(shlex.quote(part) for part in parts)


def build_resume_argv(
    *,
    provider: str,
    model: str,
    attack: str,
    user_task: str,
    injection_tasks: list[str],
    api_timeout: float,
    max_tokens: int | None = None,
) -> list[str]:
    argv = [
        sys.executable,
        "-m",
        "daily_admin_benchmark.run_model",
        "--provider",
        provider,
        "--model",
        model,
        "--attack",
        attack,
        "--user-task",
        user_task,
        "--api-timeout",
        str(api_timeout),
    ]
    if max_tokens is not None:
        argv.extend(["--max-tokens", str(max_tokens)])
    for injection_task in injection_tasks:
        argv.extend(["--injection-task", injection_task])
    return argv


def build_resume_commands(
    *,
    missing_pairs: dict[tuple[str, str], list[str]],
    provider: str,
    attack: str,
    api_timeout: float,
    max_tokens: int | None = None,
    chunk_size: int | None = None,
) -> list[str]:
    return [
        build_resume_command(
            provider=provider,
            model=model,
            attack=attack,
            user_task=user_task,
            injection_tasks=chunk,
            api_timeout=api_timeout,
            max_tokens=max_tokens,
        )
        for (model, user_task), injection_tasks in missing_pairs.items()
        for chunk in _chunks(injection_tasks, chunk_size)
    ]


def _chunks(items: list[str], chunk_size: int | None) -> list[list[str]]:
    if not items:
        return []
    if chunk_size is None or chunk_size <= 0:
        return [items]
    return [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]


def build_resume_argvs(
    *,
    missing_pairs: dict[tuple[str, str], list[str]],
    provider: str,
    attack: str,
    api_timeout: float,
    max_tokens: int | None = None,
    chunk_size: int | None = None,
) -> list[list[str]]:
    return [
        build_resume_argv(
            provider=provider,
            model=model,
            attack=attack,
            user_task=user_task,
            injection_tasks=chunk,
            api_timeout=api_timeout,
            max_tokens=max_tokens,
        )
        for (model, user_task), injection_tasks in missing_pairs.items()
        for chunk in _chunks(injection_tasks, chunk_size)
    ]


def _display_command(argv: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in argv)


def execute_resume_commands(
    argvs: list[list[str]],
    *,
    continue_on_error: bool = False,
    sleep_between: float = 0.0,
    retries: int = 0,
    retry_sleep: float = 0.0,
) -> int:
    for index, argv in enumerate(argvs, start=1):
        print(f"[{index}/{len(argvs)}] {_display_command(argv)}", flush=True)
        completed = subprocess.run(argv)
        for attempt in range(1, retries + 1):
            if completed.returncode == 0:
                break
            if retry_sleep > 0:
                print(f"Retrying after {retry_sleep:.1f}s because command failed.", flush=True)
                time.sleep(retry_sleep)
            print(f"Retry {attempt}/{retries}: {_display_command(argv)}", flush=True)
            completed = subprocess.run(argv)
        if completed.returncode != 0:
            print(f"Command failed with exit code {completed.returncode}.", flush=True)
            if not continue_on_error:
                return completed.returncode
        if sleep_between > 0 and index < len(argvs):
            print(f"Sleeping {sleep_between:.1f}s before next command.", flush=True)
            time.sleep(sleep_between)
    return 0


def build_report_command(
    *,
    provider: str,
    attack: str,
    outdir: Path,
    user_task_count: int,
    injection_task_count: int,
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "daily_admin_benchmark.report_results",
        "--provider",
        provider,
        "--attack",
        attack,
        "--user-task-count",
        str(user_task_count),
        "--injection-task-count",
        str(injection_task_count),
        "--outdir",
        str(outdir),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--missing-pairs",
        type=Path,
        default=Path("results/cross_model_user_task_0/missing_paired_runs.csv"),
        help="CSV generated by daily_admin_benchmark.report_results.",
    )
    parser.add_argument("--provider", default="siliconflow")
    parser.add_argument("--attack", default="cross_tool")
    parser.add_argument("--api-timeout", type=float, default=45.0)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Forward an optional completion-token cap to run_model.",
    )
    parser.add_argument("--execute", action="store_true", help="Run the generated commands. Default only prints them.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="With --execute, continue after a command fails instead of stopping immediately.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of grouped commands to print or run.")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Split each model/user-task group into commands with at most this many injection tasks.",
    )
    parser.add_argument(
        "--sleep-between",
        type=float,
        default=0.0,
        help="With --execute, sleep this many seconds between generated commands.",
    )
    parser.add_argument("--retries", type=int, default=0, help="With --execute, retry each failed command this many times.")
    parser.add_argument(
        "--retry-sleep",
        type=float,
        default=0.0,
        help="With --execute and --retries, sleep this many seconds before retrying a failed command.",
    )
    parser.add_argument("--refresh-report", action="store_true", help="After --execute, regenerate comparison artifacts.")
    parser.add_argument("--outdir", type=Path, default=Path("results/cross_model_user_task_0"))
    parser.add_argument("--user-task-count", type=int, default=1)
    parser.add_argument("--injection-task-count", type=int, default=50)
    args = parser.parse_args()

    missing_pairs = load_missing_pairs(args.missing_pairs)
    argvs = build_resume_argvs(
        missing_pairs=missing_pairs,
        provider=args.provider,
        attack=args.attack,
        api_timeout=args.api_timeout,
        max_tokens=args.max_tokens,
        chunk_size=args.chunk_size,
    )
    if args.limit is not None:
        argvs = argvs[: args.limit]

    if not argvs:
        print("No missing paired runs found.")
        return

    if args.execute:
        status = execute_resume_commands(
            argvs,
            continue_on_error=args.continue_on_error,
            sleep_between=args.sleep_between,
            retries=args.retries,
            retry_sleep=args.retry_sleep,
        )
        if args.refresh_report:
            report_argv = build_report_command(
                provider=args.provider,
                attack=args.attack,
                outdir=args.outdir,
                user_task_count=args.user_task_count,
                injection_task_count=args.injection_task_count,
            )
            print(f"Refreshing report: {_display_command(report_argv)}", flush=True)
            report_status = subprocess.run(report_argv).returncode
            if status == 0:
                status = report_status
        raise SystemExit(status)

    for argv in argvs:
        print(_display_command(["python", *argv[1:]]))


if __name__ == "__main__":
    main()
