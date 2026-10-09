# Lab 01 — LLM Inference Fundamentals

## Overview

**Phase:** LLM Engineering
**Day:** 1 of 15
**Estimated duration:** 2–3 hours
**Level:** Beginner to intermediate
**Primary language:** Python

### Problem Statement

Build a basic LLM-powered customer support ticket analyzer.

Given a customer message, the application sends instructions and input text to a large language model (LLM), receives a generated response, and records basic inference metrics.

The application must not invent information it has not received from an authorized source.

### Example Input

```text
My order #4821 has not arrived.
It was supposed to arrive three days ago.
Can you check the status?
```

### Expected Behavior

The model should:

1. Identify the ticket category.
2. Assign an appropriate priority.
3. Extract the order ID.
4. Draft a helpful customer response.
5. Avoid claiming to know the actual order status.

The expected behavior describes the task, not a guaranteed model output. You will evaluate the actual response during the lab.

---

## Learning Objectives

By completing this lab, you should be able to:

* Explain LLM inference and next-token prediction.
* Understand tokenization and context windows.
* Explain the role of transformers and attention.
* Distinguish system instructions from user input.
* Understand temperature and output-token limits.
* Make an LLM API request using Python.
* Inspect generated output, token usage, and request latency.
* Compare model behavior using controlled experiments.

---

## Prerequisites

* Python 3.10 or newer.
* Basic Python programming knowledge.
* Git and GitHub.
* Access to an LLM API and a configured API key.
* Familiarity with environment variables and virtual environments.

## Setup

From the repository root, install the dependencies:

```bash
pip install openai python-dotenv pytest
```

Create a `.env` file in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Use a model identifier available to your account. Never commit `.env` to Git.

Run the inference script:

```bash
python src/support_ai/day01_inference.py
```

Refer to the root README for the complete project setup.

---

## Module 1 — Understand Inference

### Concepts to Learn

**1. Tokenization**

An LLM processes text as tokens. A token may represent a complete word, a word fragment, punctuation, or another unit defined by the tokenizer.

**2. Next-token prediction**

An autoregressive LLM estimates the probability of the next token given the preceding context, then generates tokens successively.

**3. Transformer architecture**

Transformers process token representations through attention and other neural network operations to model relationships in the context.

**4. Attention**

Attention helps the model use relevant information from other tokens when computing contextual representations.

**5. Context window**

The context window limits how much input and generated content the model can handle in a request. Exact limits depend on the model and API.

**6. Inference**

Inference is the execution of a trained model to produce predictions or generated output.

### Exercise 1

Explain in your own words:

* Why does an LLM generate tokens successively?
* Why does token count differ from word count?
* Why can a long conversation exceed a model's context limit?
* How can attention help the model interpret an order ID mentioned earlier in a message?

Write your answers in your study notes.

---

## Module 2 — Run Your First Inference

Use the script:

`src/support_ai/day01_inference.py`

The script should:

1. Load configuration from environment variables.
2. Send a support ticket and instructions to the model.
3. Print the generated response.
4. Record end-to-end request latency.
5. Print input and output token counts when available.

### Exercise 2

Run the script at least once.

Inspect the response and answer:

* Did the model identify the delivery issue?
* Did it extract order ID `4821`?
* Did it invent an order status?
* Did it follow the requested response format?
* How many input and output tokens were reported?
* How long did the request take?

Record the results in `experiments.md`.

---

## Module 3 — Controlled Experiments

Perform at least two of the following experiments. Completing all three is recommended.

### Experiment A — Prompt Instructions

Compare a vague instruction with a detailed instruction.

Record whether the output becomes more relevant, complete, and consistent with the task.

### Experiment B — Output Token Limit

Compare a small output limit with a larger limit.

Observe whether the response becomes incomplete or stops before all requested fields are produced.

Explain why output limits should be chosen according to the task.

### Experiment C — Generation Variability

If the chosen model supports temperature, compare a low value with a higher value.

Keep the input and instructions constant.

Observe whether the wording, classification, or factual claims change. Repeat runs where practical.

Do not assume that low temperature guarantees correctness or that higher temperature always produces better answers.

### Experiment Rules

For every experiment:

* Change one variable at a time.
* Record the model identifier and relevant settings.
* Save or summarize the actual output.
* Record available token usage and latency.
* Separate observations from interpretations.
* Note any unsupported factual claims.

---

## Engineering Concepts

### Latency

Measure end-to-end request time using a monotonic clock, such as Python's `time.perf_counter()`.

This measurement includes network and API overhead; it is not a pure measurement of model computation.

### Token Usage

Record input and output tokens separately when the API exposes them.

Token usage can help estimate cost, but exact cost also depends on the model, pricing rules, and any additional billable features.

### Output Reliability

A plausible response is not necessarily a correct response.

For this lab, the model does not have access to an order database. It must not claim that it checked the order or assert a delivery status as fact.

---

## Acceptance Criteria

The lab is complete when:

* [ ] You can explain next-token prediction.
* [ ] You understand tokens and context windows.
* [ ] You can describe transformers and attention at a high level.
* [ ] Your Python script successfully calls the configured model.
* [ ] You inspect the generated response.
* [ ] You record latency and token usage when available.
* [ ] You complete at least two controlled experiments.
* [ ] You document observations and conclusions.
* [ ] You commit the completed lab to GitHub without exposing secrets.

## Deliverables

```text
labs/01-inference/
├── README.md
└── experiments.md
```

The Python implementation is located in:

```text
src/support_ai/day01_inference.py
```

## Completion Standard

Do not consider the lab complete merely because the API call succeeds.

You should be able to explain what the model received, what it generated, how generation settings influenced its behavior, what the metrics mean, and what the model cannot know without additional data.

## Next Lab

**Lab 02 — Model Comparison**

You will compare model configurations using a consistent evaluation dataset and investigate trade-offs among quality, latency, token usage, and cost.
