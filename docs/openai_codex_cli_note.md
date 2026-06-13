# OpenAI GPT-5.5 And Codex CLI

Updated on 2026-06-12.

GPT-5.5 is useful for repo work and review through Codex CLI, but it is not the same path as the AgentDojo model runner. The runner expects an OpenAI-compatible chat-completions API that returns tool calls for AgentDojo tools. Codex CLI is a full coding-agent interface that can read, edit, and run code in the repository.

Verified local smoke command:

```bash
codex exec \
  -m gpt-5.5 \
  -s read-only \
  -c approval_policy='"never"' \
  --ephemeral \
  'Reply with exactly: GPT55_OK'
```

Observed result:

```text
model: gpt-5.5
provider: openai
sandbox: read-only
GPT55_OK
```

Use Codex CLI for implementation review, result summarization, or repository checks. Use the benchmark runner for AgentDojo tool-use evaluation. If an OpenAI API key is available, `gpt-5.5` can also be tested through the existing OpenAI provider:

```bash
OPENAI_MODEL=gpt-5.5
python -m daily_admin_benchmark.run_model \
  --provider openai \
  --attack cross_tool \
  --user-task user_task_0 \
  --injection-task injection_task_0
```

Sources:

- OpenAI API model docs: https://developers.openai.com/api/docs/models
- Codex model docs: https://developers.openai.com/codex/models
- Codex changelog: https://developers.openai.com/codex/changelog
