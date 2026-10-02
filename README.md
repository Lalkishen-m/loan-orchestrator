## Loan Orchestrator

A stateful loan workflow orchestration system built with Python and LangGraph, designed to demonstrate reliable, human-governed workflow execution across a simulated loan processing journey.

The project focuses on state management, conditional routing, parallel verification, checkpoint-based recovery, and human-in-the-loop decision making using LangGraph.

Note: This is a simulated portfolio project. It does not connect to real banking, credit bureau, KYC, fraud, or lending systems and does not make real-world lending decisions.

🎯 Project Objective

Loan processing involves multiple stages such as application validation, identity verification, income verification, risk assessment, policy checks, and exception handling.

A traditional sequential workflow can become difficult to manage when:

Multiple verification processes need to run in parallel
Different outcomes require different workflow paths
A workflow needs to pause for human intervention
Long-running workflows need to survive interruptions
Previous workflow state needs to be recovered
Execution needs to remain traceable and auditable

Loan Orchestrator demonstrates how these challenges can be addressed using LangGraph's stateful graph-based workflow architecture.

🏗️ Architecture

The workflow follows a state-driven orchestration model:

                         START
                           │
                           ▼
                ┌─────────────────────┐
                │ Receive Application  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Validate Application │
                └──────────┬──────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                  Valid         Invalid
                    │             │
                    ▼             ▼
          ┌─────────────────┐   Reject
          │ Start           │     │
          │ Verification    │     ▼
          └────────┬────────┘    END
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       ┌─────┐ ┌────────┐ ┌─────────┐
       │ KYC │ │ Income │ │  Fraud  │
       │Check│ │ Check  │ │  Check  │
       └──┬──┘ └───┬────┘ └────┬────┘
          │        │            │
          └────────┼────────────┘
                   ▼
       ┌─────────────────────────┐
       │ Verification Status     │
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │ Risk Assessment         │
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │ Policy Check             │
       └────────────┬────────────┘
                    │
              ┌─────┴─────┐
              │           │
           Proceed     Human Review
              │           │
              ▼           ▼
             END      ┌───────────┐
                      │ interrupt │
                      └─────┬─────┘
                            │
                     Human Decision
                      Approve/Reject
                            │
                            ▼
                   Finalize Application
                            │
                            ▼
                           END
🔑 Key LangGraph Concepts Demonstrated
1. Typed State

The workflow uses a structured LoanState schema based on Python's TypedDict.

The state maintains information such as:

Application details
Current workflow stage
Verification results
Risk assessment
Policy status
Human decision

This provides a clearly defined contract for information flowing between workflow nodes.

2. Conditional Routing

Different application outcomes result in different workflow paths.

For example:

Validation
    │
    ├── Valid ──────→ Verification
    │
    └── Invalid ────→ Rejection

Similarly, the policy stage determines whether the application can proceed automatically or requires human review.

3. Parallel Execution

Multiple verification activities can execute independently:

                Start Verification
                 /       |       \
                ↓        ↓        ↓
              KYC     Income    Fraud
                \       |       /
                 \      |      /
                    ↓
          Verification Complete

This demonstrates LangGraph's ability to model fan-out and fan-in workflow patterns.

4. State Reducers

Verification results from multiple parallel branches need to be combined into a shared state.

The project uses reducers to merge verification results rather than allowing parallel nodes to overwrite each other's state.

Conceptually:

KYC Result      ──┐
                  │
Income Result  ───┼──→ Verification Results
                  │
Fraud Result   ───┘

This is important when multiple nodes update the same state field concurrently.

5. Checkpointing and Recovery

The workflow uses SQLite-based checkpointing through LangGraph.

Workflow state is persisted using:

SqliteSaver
      │
      ▼
loan_orchestrator.db

Each workflow execution is associated with a thread_id.

For example:

loan_application_102

This allows the workflow state to be recovered rather than requiring the entire process to start from the beginning.

6. Human-in-the-Loop

Applications requiring additional review can pause the workflow using LangGraph's interrupt() mechanism.

Automated Workflow
       │
       ▼
  Policy Check
       │
       ▼
 Human Review
       │
    interrupt()
       │
       ▼
Human Decision
       │
 ┌─────┴─────┐
 ▼           ▼
Approve     Reject
 │           │
 └─────┬─────┘
       ▼
   Finalize

The workflow can then resume using:

Command(resume=decision)

This demonstrates how human decisions can become part of a stateful workflow rather than being handled as an external process.

🔍 Debugging and Auditability

The workflow exposes its state and next execution point using LangGraph's state inspection capabilities.

For example:

graph.get_state(config)

The application can inspect information such as:

Current workflow state
Current stage
Risk assessment
Policy status
Human decision
Next node to execute

Combined with persistent checkpoints, this provides a foundation for traceable and auditable workflow execution.

Example execution flow:

Application received
        ↓
Application validated
        ↓
Verification started
        ↓
KYC / Income / Fraud checks
        ↓
Risk assessment
        ↓
Policy check
        ↓
Human review
        ↓
Human decision
        ↓
Application finalized
🧠 Multi-Agent / Supervisor–Worker Design Perspective

The current implementation focuses on stateful workflow orchestration using specialized workflow nodes rather than independent autonomous agents.

The architecture can naturally evolve toward a Supervisor–Worker model:

                    Supervisor
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
       KYC Worker   Income Worker  Risk Worker
           │            │            │
           └────────────┼────────────┘
                        ▼
                    Supervisor
                        │
                        ▼
                  Human Review

In such an architecture, a supervisor could coordinate specialized worker agents while maintaining a shared workflow state.

This project intentionally keeps the current implementation deterministic and explainable rather than introducing unnecessary autonomous agent behavior.

🛡️ Reliability Through Statefulness

One of the key design principles demonstrated by this project is that statefulness improves reliability in long-running workflows.

Without persistent state, an interrupted workflow could lose information about:

Which verification steps were completed
Risk assessment results
Policy decisions
Human review status

With checkpointing:

Workflow Execution
       │
       ▼
   State Update
       │
       ▼
   Checkpoint
       │
       ▼
Workflow Interrupted
       │
       ▼
State Recovered
       │
       ▼
Workflow Resumed

This makes the workflow more resilient to interruptions and particularly useful for processes involving human intervention.

🧩 Technology Stack
Technology	Purpose
Python	Application development
LangGraph	Stateful workflow orchestration
LangGraph Checkpointing	Workflow persistence and recovery
SQLite	Persistent checkpoint storage
TypedDict	Structured workflow state
VS Code	Development environment
📁 Project Structure
loan-orchestrator/
│
├── src/
│   └── loan_orchestrator/
│       ├── __init__.py
│       ├── graph.py
│       ├── nodes.py
│       └── state.py
│
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
    └── workflow-output.png
File Responsibilities

state.py

Defines the typed workflow state and structured verification results.

nodes.py

Contains the individual workflow operations such as:

Application validation
KYC verification
Income verification
Fraud verification
Risk assessment
Policy evaluation
Human review
Application finalization

graph.py

Builds and compiles the LangGraph workflow, defines routing and parallel execution, and configures checkpoint persistence.

⚙️ Getting Started
Prerequisites
Python 3.10+
Git
VS Code or another Python IDE
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd loan-orchestrator
2. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Run the workflow

From the project root:

python -m src.loan_orchestrator.graph

The workflow will execute the simulated loan journey and pause for human approval when the policy requires human review.

🧪 Example Workflow Output
Application received: 102
Application validated: 102

Starting verification for: 102

KYC verified for: 102
Income verified for: 102
Fraud check completed for: 102

Verification completed for: 102

Assessing risk for: 102

Risk assessment completed

Policy result: requires_human_review

Workflow is waiting for human review.

Enter human decision (approve/reject): approve

Human decision received: APPROVE

===== FINAL WORKFLOW STATE =====
...
🚧 Scope and Limitations

This project is intentionally a simulated loan workflow.

It does not:

Connect to real banking systems
Access real customer information
Perform real KYC
Query real credit bureaus
Perform real fraud detection
Make real lending decisions
Disburse loans

The purpose is to demonstrate workflow orchestration, state management, reliability, and human governance using LangGraph.

🚀 Future Architecture Opportunities

The current project provides a foundation for several possible extensions:

Supervisor–Worker multi-agent architecture
Subgraph-based workflow decomposition
LLM-powered document analysis
Exception classification
Automated policy interpretation
Human approval interfaces
More sophisticated audit trails
Automated workflow testing
Observability and monitoring
API-based workflow execution

These are architectural extensions rather than requirements of the current implementation.

💡 Key Takeaways

This project demonstrates how LangGraph can be used to build workflows that are:

Stateful — workflow context is maintained throughout execution
Conditional — different outcomes follow different paths
Parallel — independent verification tasks can execute concurrently
Persistent — checkpoints allow workflow state to survive interruptions
Human-governed — sensitive workflow decisions can involve human approval
Debuggable — workflow state and next execution steps can be inspected
Auditable — execution stages and decisions are explicitly represented
