# SiliconFlow Model Shortlist

Updated on 2026-06-12.

This note lists SiliconFlow models that look most useful for this repo's `daily_admin` AgentDojo suite. The suite depends on chat completions with function tools, so the main filter is simple: prefer models whose SiliconFlow page marks `Tools` as supported and whose model description mentions agent, tool, coding, office, or long-context use.

The repo does not require a SiliconFlow key unless you run live model calls.

## Configure

Add these values to `.env`:

```bash
SILICONFLOW_API_KEY=sk-your-siliconflow-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODELS=deepseek-ai/DeepSeek-V4-Flash,deepseek-ai/DeepSeek-V4-Pro,Pro/moonshotai/Kimi-K2.6,MiniMaxAI/MiniMax-M2.5,Pro/MiniMaxAI/MiniMax-M2.5,Pro/zai-org/GLM-5.1,Qwen/Qwen3-Coder-30B-A3B-Instruct,Qwen/Qwen3-30B-A3B-Instruct-2507,Qwen/Qwen3.6-27B,stepfun-ai/Step-3.5-Flash
```

The API is OpenAI compatible. This runner sends AgentDojo tools through the chat completions `tools` field. `SILICONFLOW_MODELS` is a comma-separated sweep list. If you want one model only, pass `--model` on the command line. `SILICONFLOW_MODEL` remains supported as a single-model fallback when `SILICONFLOW_MODELS` is not set.

Check configuration without making an API call:

```bash
python -m daily_admin_benchmark.run_model \
  --provider siliconflow \
  --attack cross_tool \
  --user-task user_task_0 \
  --injection-task injection_task_0 \
  --dry-run
```

Run one live pair after the key is configured:

```bash
python -m daily_admin_benchmark.run_model \
  --provider siliconflow \
  --attack cross_tool \
  --user-task user_task_0 \
  --injection-task injection_task_0 \
  --force-rerun
```

## Recommended 10

These IDs were checked against the authenticated SiliconFlow model list endpoint on 2026-06-12. A public model page can use a friendly slug that is not the exact API ID for a given account.

| Model ID | Why it fits this suite |
| --- | --- |
| `deepseek-ai/DeepSeek-V4-Flash` | Cheap first baseline. SiliconFlow lists a 1M-token context window, JSON mode, and tools. Good for comparing against the existing direct DeepSeek run. |
| `deepseek-ai/DeepSeek-V4-Pro` | Stronger DeepSeek reference model for the same task pairs. SiliconFlow lists JSON mode and tools. |
| `Pro/moonshotai/Kimi-K2.6` | Explicitly positioned for agentic workloads, long tool-call trajectories, and function calling. The authenticated API returned the `Pro/` ID. |
| `MiniMaxAI/MiniMax-M2.5` | MiniMax model trained across complex environments with strong performance in agentic tool use, search, and office work. SiliconFlow lists JSON mode and tools. |
| `Pro/MiniMaxAI/MiniMax-M2.5` | Premium MiniMax M2.5 variant returned by the model-list endpoint. Useful for checking whether the Pro route changes utility or security behavior. |
| `Pro/zai-org/GLM-5.1` | Z.ai flagship model for agentic engineering. The authenticated API returned the `Pro/` ID. |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct` | Much cheaper Qwen agentic model with a function-call-oriented design. Good for broad sweeps. |
| `Qwen/Qwen3-30B-A3B-Instruct-2507` | Cheap general Qwen baseline with improved instruction following and tool usage. |
| `Qwen/Qwen3.6-27B` | Stronger general Qwen agent-workflow candidate returned by the authenticated API. |
| `stepfun-ai/Step-3.5-Flash` | Fast and cheap, with tools supported. Good for a latency-sensitive baseline. |

## Alternates

| Model ID | Why it is not in the first 10 |
| --- | --- |
| `Qwen/Qwen3.6-35B-A3B` | Good efficient Qwen option with tools, but less directly targeted at tool-use evaluation than the Coder and 30B-A3B entries above. |
| `tencent/Hunyuan-A13B-Instruct` | The description mentions agent benchmarks, but the SiliconFlow page currently marks `Tools` as not supported, so it is not a good first choice for this AgentDojo suite. |
| `MiniMaxAI/MiniMax-M3` | Good public-page candidate, but it was not returned by this account's authenticated model-list endpoint during setup. |
| `zai-org/GLM-4.7` | Public-page candidate, but this account returned `Model disabled` for the tested API ID. |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct` | Strong public-page candidate, but this account returned `Model disabled` for the tested API ID. |
| `tencent/Hy3-preview` | Good public-page candidate, but it was not returned by this account's authenticated model-list endpoint during setup. |

## Small Sweep Command

With `SILICONFLOW_MODELS` configured, use this for a first pass before spending money on the full 250-pair matrix:

```bash
python -m daily_admin_benchmark.run_model \
  --provider siliconflow \
  --attack cross_tool \
  --user-task user_task_0 \
  --injection-task injection_task_0 \
  --force-rerun
```

For the full matrix, remove `--user-task` and `--injection-task`. That is 250 live pairs per model, so run a targeted smoke test first.

## Sources

- SiliconFlow model catalog: https://www.siliconflow.com/models
- SiliconFlow chat completions API: https://docs.siliconflow.com/en/api-reference/chat-completions/chat-completions
- SiliconFlow model list API: https://siliconflow.readme.io/reference/retrieve-a-list-of-models
- MiniMax-M2.5: https://www.siliconflow.com/models/minimax-m2-5
- DeepSeek-V4-Flash: https://www.siliconflow.com/models/deepseek-v4-flash
- DeepSeek-V4-Pro: https://www.siliconflow.com/models/deepseek-v4-pro
- Kimi-K2.6: https://www.siliconflow.com/models/kimi-k2-6
- Hy3-preview: https://www.siliconflow.com/models/hy3-preview
- GLM-5.1: https://www.siliconflow.com/models/glm-5-1
- GLM-4.7: https://www.siliconflow.com/models/glm-4-7
- Qwen3-Coder-480B-A35B: https://www.siliconflow.com/models/qwen3-coder-480b-a35b
- Qwen3-Coder-30B-A3B-Instruct: https://www.siliconflow.com/models/qwen3-coder-30b-a3b-instruct
- Qwen3-30B-A3B-Instruct-2507: https://www.siliconflow.com/models/qwen3-30b-a3b-instruct-2507
