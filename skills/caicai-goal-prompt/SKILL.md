---
name: caicai-goal-prompt
description: Turn rough user requirements, vague task ideas, bug reports, or feature requests into ready-to-use Codex /goal commands or portable agent goal prompts with clear scope, constraints, verification, iteration notes, and stop conditions. Use when the user asks to write, refine, polish, or generate a /goal instruction or goal prompt.
---

# Caicai Goal Prompt

## Overview

Convert a simple or vague request into a strong goal prompt that an AI coding agent can execute.

This skill does not execute `/goal` or manage runtime goal state. It writes high-quality goal text for platforms that support `/goal`, and a portable `Goal:` format for platforms that do not.

## Workflow

1. Identify the real objective behind the user's rough request.
2. State the expected deliverable or end state.
3. Add verification: tests, benchmarks, manual checks, screenshots, logs, or acceptance scenarios.
4. Add preservation constraints: behavior, APIs, compatibility, security, data safety, or correctness.
5. Add scope boundaries: files, services, tools, fixtures, resources, and explicit out-of-scope areas.
6. Add an iteration policy: what to record between attempts and how to choose the next experiment.
7. Add a blocked or stop condition: when to stop and what evidence to report.
8. Output one directly usable goal prompt. If useful, also output a stricter variant.

## Output Modes

### Codex Mode

Use this when the user mentions Codex, `/goal`, or wants a slash command:

```text
/goal [objective], verified by [tests/benchmarks/manual checks], while preserving [constraints]. Only use [scope boundaries/resources]. Between iterations, record [change made], [verification result], and [next best experiment]. If [blocked condition], stop and report [attempts], [evidence], [blocker], and [needed input].
```

### Portable Mode

Use this when the user wants the result for another AI platform:

```text
Goal: [objective], verified by [tests/benchmarks/manual checks], while preserving [constraints]. Only use [scope boundaries/resources]. Between iterations, record [change made], [verification result], and [next best experiment]. If [blocked condition], stop and report [attempts], [evidence], [blocker], and [needed input].
```

## Writing Rules

- Prefer one concise, directly usable goal block.
- Do not over-specify implementation details unless the user provided them or the domain requires them.
- Make completion observable: tests, build commands, browser checks, screenshots, logs, or manual scenarios.
- Include a stop condition for complex, risky, or verification-driven tasks.
- Include an iteration note when multiple attempts or experiments are likely.
- Include "do not" constraints for risky shortcuts.
- Preserve user intent even when improving wording.
- If the original request is too ambiguous, make conservative assumptions instead of asking unless wrong assumptions would be risky.
- Keep the prompt practical for an autonomous coding agent: include enough context to start, but leave room to inspect the codebase.
- Do not add a standalone diagnosis phase by default. Add investigation only when the user asks for it or the task cannot be safely attempted without evidence first.
- For frontend work, require visual verification across relevant viewports.
- For security, permissions, data deletion, billing, or production-impacting work, include explicit safety boundaries.

## Common Patterns

### Bug Fix

```text
/goal Fix [bug], verified by [reported scenario/test/log check], while preserving [existing behavior/API/security constraints]. Only use [affected modules/tests/tools]. Between iterations, record what changed, what verification showed, and the next best fix attempt. If the issue cannot be reproduced, verification cannot run, or no safe path remains, stop and report attempts, evidence, blocker, and needed input.
```

### Feature Implementation

```text
/goal Implement [feature], verified by [build/tests/end-to-end workflow], while preserving [existing behavior/API/UI conventions]. Only use [relevant modules/components/tests]. Between iterations, record what changed, verification results, and the next best implementation step. If requirements are contradictory, verification is unavailable, or implementation would require out-of-scope changes, stop and report attempts, evidence, blocker, and needed input.
```

### Refactor

```text
/goal Refactor [area] to [desired state], verified by [existing tests/static checks/review criteria], while preserving external APIs and user-visible behavior. Only use [target area and related tests]. Between iterations, record what changed, which checks passed or failed, and the next best refactor step. If tests cannot prove behavior preservation or the refactor requires unrelated rewrites, stop and report attempts, evidence, blocker, and needed input.
```

### Investigation

```text
/goal Investigate [problem] and produce a concise technical diagnosis, verified by evidence from [code/logs/tests/docs]. Only use [allowed sources/tools]. Between iterations, record what evidence was gathered, what it indicates, and the next best question to answer. If evidence is unavailable, contradictory, or access is blocked, stop and report attempts, evidence, blocker, and needed input.
```

### Performance Target

```text
/goal Bring [p95/p99/throughput/error rate target] to [number], verified by [benchmark/load test], while preserving [correctness/reliability/API behavior]. Only use [service, benchmark harness, and related tests]. Between iterations, record what changed, what the benchmark showed, and the next best experiment. If the benchmark cannot run or no viable path remains, stop and report attempted paths, evidence collected, blocker, and needed input.
```

## Examples

### Chrome Extension CORS Request

Input:

```text
帮我修复这个 Chrome 浏览器插件的跨域处理问题
```

Output:

```text
/goal 修复当前 Chrome 浏览器插件的跨域处理问题，用相关跨域请求场景、插件构建和 Chrome 控制台验证，同时保持现有功能、权限最小化和 Manifest V3 安全模型不被破坏。只能使用插件内相关的 manifest、background/service worker、content script、popup/options、runtime messaging 和相关测试。每次迭代之间，记录改了什么、请求结果或控制台显示什么、以及下一个要试的最佳修复。如果目标请求无法验证、构建跑不起来、权限范围无法合理收敛或没有安全路径可走，停下来报告试过哪些路、收集了什么证据、卡在哪里了，以及下一步需要什么输入。
```

### Checkout Performance

Input:

```text
把结账流程的 p95 延迟降到 120 毫秒以下，同时保持正确性测试全过
```

Output:

```text
/goal 把 p95 结账延迟降到 120 毫秒以下，用结账基准测试验证，同时保持正确性测试套件全过。只能用结账服务、基准测试装置和相关测试。每次迭代之间，记录改了什么、基准测试显示什么、以及下一个要试的最佳实验。如果基准测试跑不起来或者没路可走了，停下来报告试过哪些路、收集了什么证据、卡在哪里了，以及下一步需要什么输入。
```
