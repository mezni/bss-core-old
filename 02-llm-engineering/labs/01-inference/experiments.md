# Lab 01 — Inference Experiment Log

## Experiment Metadata

| Field            | Value                          |
| ---------------- | ------------------------------ |
| Date             | YYYY-MM-DD                     |
| Python version   |                                |
| Model identifier |                                |
| API provider     | OpenAI                         |
| Dataset          | Initial support-ticket example |
| Environment      | Local development              |

## Baseline Run

### Input

```text
My order #4821 has not arrived.
It was supposed to arrive three days ago.
Can you check the status?
```

### Instructions

```text
You are a customer support ticket analyzer.

Classify the ticket and draft a concise response.
Do not invent an order status or claim to have checked a database.

Return:
1. Category
2. Priority
3. Order ID, if present
4. Draft reply
```

### Baseline Results

| Metric                       | Observed value |
| ---------------------------- | -------------- |
| Input tokens                 |                |
| Output tokens                |                |
| End-to-end latency (seconds) |                |
| Response complete?           |                |
| Correct category?            |                |
| Correct order ID?            |                |
| Unsupported status claim?    |                |
| Follows instructions?        |                |

### Actual Model Output

Paste the actual response here. Do not replace it with an idealized response.

```text
```

### Initial Observations

* What did the model do correctly?
* What was missing or incorrect?
* Did it follow all instructions?
* Did it make any unsupported claims?

**Notes:**

---

## Experiment A — Prompt Engineering

### Objective

Determine whether more explicit instructions improve the usefulness and consistency of the generated response.

### Hypothesis

A prompt specifying the required fields and prohibiting unsupported order-status claims will produce a more useful response than a vague instruction.

### Independent Variable

Prompt instructions.

### Controlled Variables

* Model identifier.
* Ticket text.
* Generation settings.
* Output-token limit.
* Other API parameters.

### Procedure

1. Run the ticket using the baseline instructions.
2. Run the same ticket using a more explicit prompt.
3. Save both responses.
4. Compare instruction adherence and unsupported claims.

### Results

| Metric                  | Baseline prompt | Revised prompt |
| ----------------------- | --------------- | -------------- |
| Required fields present |                 |                |
| Correct category        |                 |                |
| Correct order ID        |                 |                |
| Unsupported claims      |                 |                |
| Response usefulness     |                 |                |
| Latency (seconds)       |                 |                |
| Input tokens            |                 |                |
| Output tokens           |                 |                |

### Actual Outputs

**Baseline:**

```text
```

**Revised:**

```text
```

### Conclusion

* Did the revised prompt improve the response?
* Did it introduce additional tokens?
* Did it eliminate all errors?
* What would you change next?

**Conclusion:**

---

## Experiment B — Output Token Limit

### Objective

Observe how the output-token limit affects response completeness.

### Hypothesis

A limit that is too small may prevent the model from completing the requested output.

### Independent Variable

`max_output_tokens`.

### Controlled Variables

Keep the prompt, ticket, model, and other supported settings constant.

### Procedure

1. Run with a small output limit, such as 30 tokens.
2. Run again with a larger limit, such as 200 tokens.
3. Record the output and any completion-status metadata exposed by the API.
4. Check whether all requested fields are present.

### Results

| Metric                            | Small limit | Larger limit |
| --------------------------------- | ----------- | ------------ |
| Configured output-token limit     | 30          | 200          |
| Actual output tokens              |             |              |
| All requested fields present?     |             |              |
| Response truncated or incomplete? |             |              |
| Completion status                 |             |              |
| Latency (seconds)                 |             |              |

### Conclusion

Explain whether the smaller limit affected completeness and how the application should detect incomplete output.

**Conclusion:**

---

## Experiment C — Generation Variability

### Objective

Observe how generation settings influence output variability.

### Hypothesis

When supported, a higher temperature may increase variation in wording and sampled output. It does not necessarily improve correctness.

### Independent Variable

Temperature, if supported by the selected model and endpoint.

### Controlled Variables

* Model identifier.
* Ticket.
* Instructions.
* Output-token limit.
* Other generation parameters.

### Procedure

1. Run with a low temperature, such as `0.1`, if supported.
2. Run with a higher temperature, such as `0.8`, if supported.
3. Repeat runs when practical.
4. Compare classification, wording, completeness, and factual claims.

If the selected model does not support temperature, document that limitation and compare repeated runs using supported settings.

### Results

| Metric                           | Low setting | Higher setting |
| -------------------------------- | ----------- | -------------- |
| Temperature or supported setting |             |                |
| Category                         |             |                |
| Order ID                         |             |                |
| Wording changed?                 |             |                |
| Unsupported claims               |             |                |
| Input tokens                     |             |                |
| Output tokens                    |             |                |
| Latency (seconds)                |             |                |

### Conclusion

* Did the output change?
* Was the classification stable?
* Did any output introduce unsupported information?
* Which settings would you use for this task, and why?

**Conclusion:**

---

## Final Day 1 Review

### Conceptual Understanding

Answer without consulting the lab README.

**1. Next-token prediction**

Explain how an autoregressive LLM generates a response.

**Answer:**

**2. Tokenization**

Why is the number of tokens not necessarily equal to the number of words?

**Answer:**

**3. Context window**

What happens when the total request exceeds the model's context limit?

**Answer:**

**4. Attention**

What role does attention play in processing contextual information?

**Answer:**

**5. Temperature**

Why does a higher temperature not necessarily mean a better answer?

**Answer:**

**6. Output-token limits**

How can a small output-token limit affect structured or multi-part responses?

**Answer:**

**7. Reliability**

Why is a plausible response not necessarily a factually correct response?

**Answer:**

**8. Metrics**

Why should an AI engineer measure token usage and end-to-end latency?

**Answer:**

---

## Key Findings

Summarize what you learned in 3–5 bullet points.

*
*
*

## Issues Encountered

Record API errors, setup problems, unsupported settings, or unexpected model behavior.

| Issue | Root cause | Resolution |
| ----- | ---------- | ---------- |
|       |            |            |

## Day 1 Completion Checklist

* [ ] The inference script runs successfully.
* [ ] The baseline output is recorded.
* [ ] At least two controlled experiments are complete.
* [ ] Token usage and latency are recorded where available.
* [ ] The knowledge-check questions are answered.
* [ ] No secrets are committed to GitHub.
* [ ] Findings are committed with the lab.

## Suggested Commit

```bash
git add labs/01-inference/
git commit -m "docs: add day 1 inference lab and experiments"
git push
```

The experiment log should contain observed results, not invented or estimated measurements presented as actual API results.
