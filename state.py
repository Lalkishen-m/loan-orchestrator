"""
This file defines the shared state of our loan-processing workflow.
The state is the information that travels through the LangGraph.
Every node in our graph can read the state and update parts of it.
"""
from typing import TypedDict, Annotated

class VerificationResult(TypedDict):
    """
    Represents the result produced by one
    verification component.
    """

    check_type: str
    status: str
    source: str
    details: str


def merge_verification_results(
    existing: list[VerificationResult],
    new: list[VerificationResult],
) -> list[VerificationResult]:
    """
    Merge verification results produced by
    different verification nodes.
    """

    return existing + new

class LoanState(TypedDict):
    """
    Shared state for the Loan Orchestrator.
    """

    # -------------------------
    # Application information
    # -------------------------

    application_id: str
    applicant_name: str
    loan_amount: float

    # -------------------------
    # Workflow information
    # -------------------------

    current_stage: str
    status: str

    # -------------------------
    # Verification information
    # -------------------------

    kyc_status: str
    income_status: str
    fraud_status: str

    verification_results: Annotated[
    list[VerificationResult],
    merge_verification_results,
]
  # -------------------------
  # Risk information
  # -------------------------

    risk_score: float
    risk_category: str
  
  # -------------------------
  # Policy information
  # -------------------------

    policy_status: str
    policy_reason: str
  
  # -------------------------
  # Human review
  # -------------------------
    human_decision: str
