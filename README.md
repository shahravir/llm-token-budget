# llm-token-budget

Companion code for **Token Budget Discipline: A Developer's Playbook for the Quota Era**.

Blog: [`BLOG.md`](BLOG.md)

Related reading:

- [Patterns for Context Engineering in Agentic Applications](https://www.linkedin.com/pulse/patterns-context-engineering-agentic-applications-ravi-shah-uja4e) — deeper patterns (compression, hierarchy, progressive disclosure, external memory)
- [Medium @shah.ravir](https://medium.com/@shah.ravir)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Samples

| Directory | What it demonstrates |
|-----------|----------------------|
| [`samples/01-context-budget`](samples/01-context-budget) | Fit messages under a token budget (priority + truncation) |
| [`samples/02-model-router`](samples/02-model-router) | Route by task type to local / mid / frontier |
| [`samples/03-token-monitor`](samples/03-token-monitor) | Estimate tokens and append to a usage log |
| [`samples/04-progressive-disclosure`](samples/04-progressive-disclosure) | Repo index first, full files on demand |
| [`samples/05-local-ollama-router`](samples/05-local-ollama-router) | Ollama for small tasks; escalation flag |
| [`samples/06-compressed-delegation`](samples/06-compressed-delegation) | Cavecrew-style compressed findings |

## Skills

- [`skills/caveman-lite/SKILL.md`](skills/caveman-lite/SKILL.md) — copy into `.cursor/skills/` or Claude Code skills to reduce verbose agent output

## License

MIT
