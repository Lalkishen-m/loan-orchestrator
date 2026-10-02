### Loan Orchestrator

A stateful loan workflow orchestration system built with Python and **LangGraph**, designed to demonstrate reliable, human-governed workflow execution across a simulated loan processing journey.

The project focuses on **state management, conditional routing, parallel verification, checkpoint-based recovery, and human-in-the-loop** decision making using LangGraph.

Note: This is a simulated portfolio project. It does not connect to real banking, credit bureau, KYC, fraud, or lending systems and does not make real-world lending decisions.

## 🎯 Project Objective

Loan processing involves multiple stages such as application validation, identity verification, income verification, risk assessment, policy checks, and human approvals. Loan Orchestrator uses LangGraph to model these stages as a stateful workflow, enabling parallel verification, conditional routing, checkpoint-based recovery, and human-in-the-loop decision-making. The project demonstrates how complex, long-running business workflows can be made more structured, reliable, auditable, and fault-tolerant using graph-based orchestration.

## 🏗️ Architecture

The workflow follows a state-driven orchestration model:

                         START
                           │
                           ▼
                ┌─────────────────────┐
                │ Receive Application │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Validate Application│
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
          │        │           │
          └────────┼───────────┘
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
       │ Policy Check            │
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
                           
## 🔑 Key LangGraph Concepts Demonstrated
**1. Typed State**

The workflow uses a structured LoanState schema based on Python's TypedDict.

The state maintains information such as:

Application details
Current workflow stage
Verification results
Risk assessment
Policy status
Human decision

This provides a clearly defined contract for information flowing between workflow nodes.

**2. Conditional Routing**

Different application outcomes result in different workflow paths.

For example:

Validation
    │
    ├── Valid ──────→ Verification
    │
    └── Invalid ────→ Rejection

Similarly, the policy stage determines whether the application can proceed automatically or requires human review.

**3. Parallel Execution**

Multiple verification activities can execute independently. This demonstrates LangGraph's ability to model fan-out and fan-in workflow patterns.

**4. State Reducers**

Verification results from multiple parallel branches need to be combined into a shared state. The project uses reducers to merge verification results rather than allowing parallel nodes to overwrite each other's state. This is important when multiple nodes update the same state field concurrently.

**5. Checkpointing and Recovery**
The workflow uses SQLite-based checkpointing through LangGraph. This allows the workflow state to be recovered rather than requiring the entire process to start from the beginning.
Each workflow execution is associated with a thread_id.
For example: loan_application_102

**6. Human-in-the-Loop**

Applications requiring additional review can pause the workflow using LangGraph's interrupt() mechanism.
The workflow can then resume using:Command(resume=decision)
This demonstrates how human decisions can become part of a stateful workflow rather than being handled as an external process.

## 🔍 Debugging and Auditability

The workflow exposes its state and next execution point using LangGraph's state inspection capabilities.
For example: graph.get_state(config)
The application can inspect information such as:
Current workflow state
Current stage
Risk assessment
Policy status
Human decision
Next node to execute
Combined with persistent checkpoints, this provides a foundation for traceable and auditable workflow execution.

## 🧠 Multi-Agent / Supervisor–Worker Design Perspective

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

## 🧪 Example Workflow Output
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
