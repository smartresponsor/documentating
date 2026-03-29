---
title: "Do Not Scale the Imitation of a Human"
description: "Why the future of AI automation belongs to orchestration, deterministic execution, and reproducible protocol—not to scaling browser-level imitation of a person."
date: 2026-03-29
author: "Oleksandr"
tags:
  - AI
  - agents
  - automation
  - Playwright
  - LLM
  - architecture
  - engineering
---

# Do Not Scale the Imitation of a Human

There is a seductive illusion at the center of the current AI wave.

A model opens a browser. It clicks a button. It expands a hidden panel. It copies text. It downloads a file. It navigates to the next page. It looks, at first glance, like intelligence. It looks like autonomy. It looks like the machine has learned to “use a computer” the way a person does.

And that is precisely why so many people overestimate the wrong thing.

The breakthrough is not that the machine can imitate a human at the interface level.

The breakthrough begins when we stop forcing it to.

That is the deeper lesson emerging from serious AI engineering work right now. The strongest systems are not the ones that most convincingly mimic a user moving through a website. The strongest systems are the ones that understand where imitation is useful, where it becomes wasteful, and where it should be abandoned in favor of a better operational layer.

This is not merely an optimization insight. It is an architectural shift.

## The glamour phase of AI automation

The first phase of modern AI automation is almost always theatrical.

A model is attached to a browser. It can see the page. It can interpret the interface. It can type, click, scroll, and respond to the unexpected. This feels magical because it collapses the distance between human interaction and machine action. The browser becomes a stage, and the model becomes a digital operator.

This stage matters. It is not fake progress.

Browser-level control is extremely useful for:

- exploring unfamiliar systems,
- validating whether an interface can be automated at all,
- handling dynamic pages and non-standard flows,
- discovering hidden dependencies in real workflows,
- testing where structured access ends and messy reality begins.

In that exploratory phase, AI-driven browser control is often the fastest way to learn what the real problem is.

But the glamour phase creates a dangerous misconception: that scaling browser imitation is equivalent to scaling automation.

It is not.

In many cases, it is the exact opposite.

## When clicking becomes the bottleneck

At small scale, browser imitation feels efficient enough. A model can open a page, reveal a transcript, copy the content, save it somewhere, and move on. If you do this once or twice, the approach looks valid. If you do it across dozens or hundreds of pages, the weaknesses become structural.

Everything starts to hurt at once.

Latency compounds. Sequential action chains become expensive. Rate limits appear in strange places. Large outputs do not fit comfortably through model-mediated channels. Data transfer becomes fragile. Special characters break serialization. Context windows become accidental transport layers. Files are no longer “saved”; they are manually ferried through an intelligence layer that was never designed to be a filesystem or a bulk transfer bus.

The model becomes the bottleneck not because it is weak, but because it is being used for the wrong job.

And this is the moment where many teams make the wrong decision.

They ask how to make the imitation faster.

They should be asking how to stop depending on imitation.

## The wrong question and the right question

The wrong question is:

> How do we make the agent click through the interface more efficiently?

The right question is:

> What is the system’s real operational entry point?

That single shift changes everything.

A user interacts through the UI because that is the access path available to a human. A machine is not obligated to inherit that limitation.

The interface is often only the surface layer of a deeper mechanism:

- an API call,
- a network request,
- a download event,
- a structured file,
- an object in storage,
- a background job,
- a CDN-delivered asset,
- a server-side state transition,
- a form submission with a deterministic payload,
- or some other artifact that the browser merely presents.

The mature engineer does not ask how to click better.

The mature engineer asks where the system is actually doing the work.

That is the difference between UI choreography and architecture.

## The real lesson: change the layer, not just the speed

Once a task becomes repetitive, high-volume, or strategically important, the priority should shift from interface imitation to layer selection.

If the workflow can be executed at a lower and more direct layer, that is usually where the long-term solution belongs.

If data can be captured before it is rendered, do not wait for a model to read it off the screen.

If a browser can directly observe a download or network response, do not make the model manually transcribe it into a file.

If a deterministic process can transform the data, do not ask a model to act as a fragile conversion engine.

If a batch job can run in parallel, do not force the system through a single-threaded chain of “look, decide, click, wait, copy, save.”

In other words: the path toward scalable AI automation is usually not a better simulation of a person.

It is a better selection of the machine-native level of interaction.

## Why the LLM should not be your data pipeline

This is the point where the role of the model has to be redefined.

A great deal of AI-system failure comes from assigning the LLM tasks that belong to infrastructure.

A model is not a storage system.

It is not a message queue.

It is not a reliable bulk transfer mechanism.

It is not an ideal parser for large repetitive datasets.

It is not a download manager.

It is not a filesystem adapter.

And it should not be treated as a universal tunnel through which all operational work must pass.

That pattern can work on tiny tasks. It collapses on larger ones.

The real value of an LLM lies elsewhere.

A model is valuable when the system needs judgment:

- deciding which strategy to use,
- interpreting ambiguous context,
- selecting tools,
- handling edge cases,
- summarizing content,
- drafting descriptions,
- identifying anomalies,
- choosing what matters,
- routing subtasks,
- coordinating multi-step intent.

That is where intelligence belongs.

Not in acting as a human-shaped pipe for data.

## Intelligence should orchestrate, not manually carry boxes

A mature AI system becomes more understandable once you divide it into layers.

One clean formulation looks like this:

- **LLM as intelligence**
- **Browser automation or external tools as hands**
- **Deterministic scripts as muscles and bones**
- **Protocol as memory, discipline, and reproducibility**

This division matters because it solves the most common confusion in AI automation.

People often ask, “What should the model do?”

The better question is, “What should the model *not* do?”

The model should not spend its cognitive budget on repeatable, mechanical, high-volume work that conventional software performs more reliably.

It should orchestrate.

It should decide.

It should route.

It should synthesize.

It should supervise.

And it should leave the heavy lifting to code that is cheaper, faster, more stable, more parallelizable, and easier to validate.

This is not a compromise. It is the essence of good system design.

## Why deterministic software gets stronger when AI gets involved

There is a strange rhetorical mistake in the market right now.

Some people imagine that using more code somehow means using less AI. As if handing work back to deterministic tooling is a retreat from intelligence.

In practice, the opposite is true.

The better the deterministic layer is, the more effective the AI layer becomes.

A model attached to vague, fragile, ad hoc tooling becomes erratic. A model attached to a disciplined, predictable, well-instrumented environment becomes useful.

When the surrounding software layer is strong, the model can focus on the tasks where it actually creates leverage.

It can:

- choose the right extraction path,
- notice when a flow changes,
- identify whether an exception is meaningful,
- classify outputs,
- produce summaries,
- map content into structure,
- prioritize next actions,
- escalate uncertain cases to a human.

This is why real AI engineering is not about replacing software with a model. It is about building a stronger software frame around the model.

The more disciplined the frame, the more powerful the intelligence layer becomes.

## The most underestimated layer is protocol

There is another mistake people make when they talk about successful automation.

They confuse a one-time win with a reusable capability.

Getting a task to work once is not yet a system.

What turns it into a system is protocol.

Protocol is the part that answers questions like:

- How does the process start?
- What exactly is the input?
- Where are artifacts stored?
- How are intermediate states tracked?
- What happens if the run fails halfway through?
- How does a new session continue without repeating old work?
- What is logged?
- How are retries handled?
- How are summaries generated?
- How are outputs validated?
- How is quality checked?
- How does another person rerun the process?
- How does another agent inherit the state?

Without answers to those questions, you do not have a technology. You have an episode.

Protocol is what makes a workflow transferable. It is what makes an automation stack adoptable by someone who did not personally invent it. It is what makes the result not merely clever, but operational.

In many ways, protocol is what transforms AI work from improvisation into engineering.

## Why “autonomy” is often an architectural mirage

The market loves the word *autonomy* because it sounds futuristic.

But autonomy, by itself, is an unstable metric.

A system can look autonomous while being architecturally poor. It can appear impressive in a demo and still be unscalable, untraceable, unrepeatable, or unsafe.

A model that clicks around a browser for an hour is not necessarily evidence of maturity. It may just be evidence that the surrounding architecture is forcing intelligence to compensate for a missing operations layer.

This is why apparent autonomy can be misleading.

The more important questions are:

- Does the system use the correct layer of interaction?
- Does it separate reasoning from execution?
- Can it run in parallel?
- Can it store state externally?
- Can it recover from failure?
- Can it be audited?
- Can it be transferred?
- Can its outputs be validated?
- Can it be reused without rediscovering the process every time?

A system with modest-looking AI and excellent architecture will usually outperform a theatrically autonomous system built on the wrong level of abstraction.

That is one of the most important truths of this era.

## The browser is a tool, not a philosophy

The current wave of browser-use agents has produced an important capability. But it has also encouraged a conceptual error: treating the browser itself as the ideal medium of automation.

It is not.

The browser is one interface to a system. Sometimes it is the only practical one. Sometimes it is the best exploratory one. Sometimes it is the most universal one.

But it is not automatically the best production layer.

The browser should be treated as a tool, not as a philosophy.

If the browser is the right layer, use it.

If it is only a discovery instrument on the path to a deeper interface, move past it.

If it remains necessary for edge cases, keep it where it belongs: in the exception path, not at the center of the entire throughput model.

This is a very important distinction.

Many teams are currently trying to build the future by scaling the wrong middle layer. They think the answer is “more agent,” “more browser,” “more autonomy,” “more clicks without humans.”

But if the architecture still routes everything through the most expensive and least stable layer, that future remains fragile.

## A more durable pattern

A more durable pattern is beginning to emerge.

It is not mystical. It is almost disappointingly practical.

1. Use the browser or interface-level agent to explore, discover, and validate access paths.
2. Identify the system’s real operational surfaces.
3. Move bulk extraction, transformation, storage, retries, and parallel execution into deterministic code.
4. Use the model for strategy, interpretation, summarization, routing, supervision, and exception handling.
5. Wrap the whole thing in a protocol that another person—or another agent—can rerun without invention.

That is the pattern that scales.

Not because it looks magical, but because it stops wasting intelligence on labor that code should perform.

## This is not anti-agent. It is pro-architecture.

Some people may read this argument as a rejection of agents.

It is not.

It is a rejection of architectural laziness disguised as agent enthusiasm.

Agents are real.

Browser use is real.

LLM orchestration is real.

Tool-using models are real.

What is changing is our understanding of where each of those belongs.

The next serious phase of the field will not be won by those who can produce the most impressive browser demos. It will be won by those who can compose layered systems where intelligence is used deliberately, execution is deterministic wherever possible, and protocol makes the capability portable.

That is a much less cinematic story.

It is also a much more important one.

## The practical rule set

If all the noise is removed, the emerging rule set is surprisingly simple:

### 1. Do not imitate a human where you can describe a system.
If a process has a machine-native access path, use it.

### 2. Do not route data through a model where code can handle it directly.
Models should interpret and coordinate, not act as fragile transport channels.

### 3. Do not confuse autonomy with architecture.
A long-running demo is not the same thing as an operationally sound system.

### 4. Do not keep bulk work at the UI layer if it can move down-stack.
The lower, cleaner, and more deterministic the layer, the stronger the system usually becomes.

### 5. Do not call a task solved until it has a reproducible protocol.
If it cannot be rerun, handed off, audited, and resumed, it is not finished.

## The real shift

The real shift in AI automation is not that machines are finally learning to act like users.

The real shift is that we are finally learning how to stop designing them as users.

That is the difference between spectacle and systems.

That is the difference between a browser puppet and an operational architecture.

And that is why the future does not belong to scaling the imitation of a human.

It belongs to building systems in which:

- intelligence reasons,
- tools act,
- code executes deterministically,
- and protocol makes the whole thing durable.

Once you see that clearly, a great deal of current AI hype becomes much easier to decode.

The question is no longer whether a model can click through a workflow.

The question is whether the workflow was designed at the right layer in the first place.

That is where the real leverage begins.
