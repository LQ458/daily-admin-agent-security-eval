# Eval Design Note

This note explains the evaluation idea behind the `daily_admin` suite.

Static prompt injection tests are useful. They isolate a clear failure mode and make results easy to reproduce. They can also miss failures that only appear when an agent is doing a normal tool use task: reading app content, deciding which instruction source to trust, calling tools, and changing state.

The daily admin setting is small, but it has the shape I wanted to study. A note can be useful input for a task list. A course page can be needed for a study plan. A shift note can justify a time entry. An access review task can require approving one prompt while denying another. In each case, a useful action and an unsafe injected action may use the same tool family.

That means the benchmark should not score only whether an injected action happened. It should also score whether the agent completed the user's original task. A defense that blocks every write may reduce injection success, but it also fails the utility side of the evaluation.

The suite uses paired outcomes:

- **Task success:** did the agent complete the user's requested workflow?
- **Injection success:** did the agent perform the injected action?
- **Over-defense:** did the agent refuse or avoid tools needed for the benign task?
- **Defense consistency:** did the same defense behave similarly across related tasks?

The examples cover a few failure modes:

- **Indirect prompt injection:** retrieved app content asks the agent to create an unrelated task or submit unintended text.
- **Instruction hierarchy failure:** app content is treated as authority rather than data.
- **Tool overreach:** the agent changes settings, payout state, workspace membership, or report contents beyond the user's task.
- **Context contamination:** a note changes later task state instead of staying limited to the current workflow.

The main open question is how to balance realism with reproducibility. More app state and richer workflows can reveal failures that flat prompt tests miss. They also make the benchmark harder to inspect, maintain, and compare across runs. This project takes a narrow middle path: a resettable AgentDojo suite with simple simulated tools, explicit ground truth checks, and model runs that can be repeated.
