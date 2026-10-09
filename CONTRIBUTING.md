# Contributing Guidelines

Thank you for your interest in the **AI Architect — System Design Lab**.

This repository is a hands-on learning project focused on system design principles and their application to production AI systems. Contributions should improve technical accuracy, documentation quality, reproducibility, or the practical value of the exercises.

## 1. Contribution Goals

Contributions should help achieve one or more of the following goals:

* Improve the clarity and correctness of system design concepts.
* Add practical exercises or engineering experiments.
* Improve architecture diagrams and technical documentation.
* Demonstrate design trade-offs with concrete examples.
* Add tests or improve existing implementations.
* Document reliability, scalability, security, and performance considerations.

## 2. Repository Structure

Follow the existing directory structure when adding files.

```text
.
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── api-design.md
│   ├── database-design.md
│   ├── capacity-estimation.md
│   ├── reliability.md
│   ├── security.md
│   └── adr/
├── diagrams/
├── src/
├── tests/
└── experiments/
```

Guidelines:

* `docs/`: System requirements, architecture, and technical decisions.
* `diagrams/`: Architecture and data-flow diagrams.
* `src/`: Small implementations that support the learning objectives.
* `tests/`: Automated tests.
* `experiments/`: Isolated exercises and practical investigations.
* `docs/adr/`: Architecture Decision Records.

Place new files in the directory that best matches their purpose.

## 3. Types of Contributions

### Documentation

Documentation should be accurate, concise, and easy to reproduce.

Include:

* The problem being addressed.
* Relevant technical concepts.
* Design alternatives.
* Benefits and limitations.
* Links to authoritative references when appropriate.

### Architecture diagrams

Diagrams should clearly communicate component responsibilities, communication paths, and important system boundaries.

Use Mermaid or diagrams.net when practical. Keep diagrams consistent with the accompanying architecture documentation.

### Code and experiments

Code should demonstrate a specific engineering concept rather than introduce unnecessary complexity.

Requirements:

* Use descriptive names and clear structure.
* Include error handling where appropriate.
* Add tests for important behavior.
* Avoid committing secrets, credentials, API keys, or personal data.
* Document setup instructions and assumptions.
* Keep experiments reproducible.

### Architecture Decision Records

Use ADRs to document significant architectural choices.

Each ADR should include:

1. Context and problem.
2. Decision.
3. Alternatives considered.
4. Consequences and trade-offs.
5. Status.

Suggested filename:

`docs/adr/001-initial-architecture.md`

## 4. Development Setup

### Prerequisites

* Python 3.11 or later.
* Git.
* A virtual environment.
* A code editor.

### Clone the repository

```bash
git clone <your-repository-url>
cd ai-architect-system-design-lab
```

### Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

When the project dependencies have been defined:

```bash
pip install -r requirements.txt
```

## 5. Branching Strategy

Use short-lived branches for individual changes.

Suggested naming conventions:

| Change type    | Branch example                    |
| -------------- | --------------------------------- |
| New feature    | `feature/add-health-endpoint`     |
| Documentation  | `docs/improve-architecture-guide` |
| Bug fix        | `fix/api-validation`              |
| New experiment | `experiment/redis-caching`        |
| Tests          | `test/health-endpoint`            |

Example:

```bash
git switch -c docs/improve-architecture-guide
```

Keep each branch focused on one logical change.

## 6. Commit Message Convention

Write clear commit messages that describe the change.

Use these prefixes:

* `feat:` — New functionality.
* `fix:` — Bug fixes.
* `docs:` — Documentation changes.
* `test:` — Tests.
* `refactor:` — Code restructuring without behavior changes.
* `experiment:` — Learning experiments.
* `chore:` — Maintenance tasks.

Examples:

```text
docs: add system requirements
feat: implement health endpoint
test: cover health endpoint response
experiment: compare caching strategies
docs: record database architecture decision
```

Prefer small, meaningful commits over large commits containing unrelated changes.

## 7. Testing and Validation

Before submitting a change, verify the relevant files and behavior.

For Python changes, run:

```bash
pytest
```

For documentation-only changes, verify:

* Markdown formatting is correct.
* Internal file paths point to the intended files.
* Commands and code snippets are syntactically correct.
* Diagrams render correctly.
* Statements distinguish measured results from assumptions.

Do not claim that tests pass unless you have actually run them.

## 8. Pull Request Process

Before opening a pull request:

1. Confirm that your branch contains only related changes.
2. Review your diff for accidental edits or secrets.
3. Run the relevant tests.
4. Update documentation when behavior or architecture changes.
5. Explain the motivation and impact of the change.

A pull request should describe:

* **Problem:** What needs improvement?
* **Solution:** What changed?
* **Trade-offs:** What alternatives were considered?
* **Validation:** What tests or checks were performed?
* **Documentation:** Which documents or diagrams were updated?

For a personal learning repository, the same checklist can be used when reviewing your own work before merging.

## 9. Code Quality and Security

All contributions should follow these principles:

* Prefer simple designs over unnecessary abstraction.
* Make assumptions and limitations explicit.
* Keep credentials in environment variables or an appropriate secrets manager.
* Never commit `.env` files containing real secrets.
* Validate external inputs.
* Apply least-privilege access principles.
* Avoid logging sensitive information.
* Identify security implications when proposing architectural changes.

## 10. Learning and Technical Discussions

Questions, corrections, and alternative design proposals are welcome.

When proposing a different architecture, explain why it is preferable under the stated requirements. Discuss relevant factors such as scalability, availability, latency, consistency, complexity, security, and cost.

There is not always one universally correct architecture. Design choices should be justified by the system's constraints.

## 11. Definition of a Good Contribution

A contribution is ready when it is:

* Technically accurate.
* Clearly documented.
* Consistent with the repository structure.
* Reproducible where applicable.
* Tested when code behavior changes.
* Explicit about assumptions and trade-offs.

Thank you for helping make this System Design Lab a useful engineering learning resource.

---

**Project:** AI Architect Roadmap
**Phase:** System Design
**Repository:** `ai-architect-system-design-lab`

