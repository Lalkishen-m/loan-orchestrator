"""
This file contains the individual pieces of work
performed by our LangGraph workflow.
"""

from .state import LoanState
from langgraph.types import interrupt

def receive_application(state: LoanState) -> dict:
    print(
        f"Application received: {state['application_id']}"
    )

    return {
        "current_stage": "application_received",
        "status": "received",
    }


def validate_application(state: LoanState) -> dict:
    application_id = state["application_id"]
    applicant_name = state["applicant_name"]
    loan_amount = state["loan_amount"]

    # Validate application ID.
    if not application_id.strip():
        return {
            "current_stage": "validation_failed",
            "status": "invalid",
        }

    # Validate applicant name.
    if not applicant_name.strip():
        return {
            "current_stage": "validation_failed",
            "status": "invalid",
        }

    # Validate loan amount.
    if loan_amount <= 0:
        return {
            "current_stage": "validation_failed",
            "status": "invalid",
        }

    print(
        f"Application validated: {application_id}"
    )

    return {
        "current_stage": "application_validated",
        "status": "ready_for_processing",
    }

def decide_after_validation(state: LoanState) -> str:
    """
    Decide where the workflow should go after validation.

    This function does not perform the validation itself.

    It only looks at the current state and decides
    which path the graph should take.
    """

    if state["status"] == "ready_for_processing":
        return "valid"

    return "invalid"

def reject_application(state:LoanState) -> dict:

    print(
        f"Application rejected during validation: "
        f"{state['application_id']}"
    )

    return {
        "current_stage": "validation_failed",
        "status": "rejected",
    }
def verify_documents(state: LoanState) -> dict:
    application_id = state["application_id"]

    print(
        f"Documents verified for: {application_id}"
    )

    return {
        "current_stage": "documents_verified",
        "status": "verification_complete",
        "kyc_status": "verified",
    }

def verify_income(state: LoanState) -> dict:

    application_id = state["application_id"]

    print(
        f"Income verified for: {application_id}"
    )

    return {
         "income_status":"verified",
    "verification_results": [
        {
            "check_type": "Income",
            "status": "verified",
            "source": "simulated_income_system",
            "details": "Income verification completed successfully",
        }
    ],
}

def verify_kyc(state: LoanState) -> dict:
    application_id = state["application_id"]

    print(
        f"KYC verified for: {application_id}"
    )

    return {
    "kyc_status":"verified",
    "verification_results": [
        {
            "check_type": "KYC",
            "status": "verified",
            "source": "simulated_kyc_system",
            "details": "Identity verification completed successfully",
        }
    ],
}

def verify_fraud(state: LoanState) -> dict:

    application_id = state["application_id"]

    print(f"Fraud check completed for: {application_id}")

    return {
        "fraud_status": "Cleared",
        "verification_results": [
            {
                "check_type": "FRAUD",
                "status": "clear",
                "source": "simulated_fraud_system",
                "details": "No suspicious activity detected",
            }
        ]
    }

def start_verification(state: LoanState) -> dict:
    """
    Start the verification stage.

    This node acts as a fan-out point,
    allowing KYC and income verification
    to run as separate branches.
    """

    print(
        f"Starting verification for: "
        f"{state['application_id']}"
    )

    return {
        "current_stage": "verification_started",
    }

def check_verification_status(state: LoanState) -> dict:
    """
    Check whether all required verification
    activities have completed.
    """

    kyc_status = state["kyc_status"]
    income_status = state["income_status"]
    fraud_status = state ["fraud_status"]

    if (
        kyc_status == "verified"
        and income_status == "verified" 
        and fraud_status == "Cleared"
    ):
        return {
            "current_stage": "verification_complete",
            "status": "ready_for_risk_assessment",
        }

    return {
        "current_stage": "verification_incomplete",
        "status": "verification_pending",
    }

def assess_risk(state: LoanState) -> dict:
    """
    Perform a simulated risk assessment.

    This is intentionally deterministic.
    It does not call a real credit bureau
    or make a real lending decision.
    """
    print(
        f"Assessing risk for: "
        f"{state['application_id']}"
    )

    risk_score = 0

    for result in state["verification_results"]:

    # A verification that is not successful
    # increases the simulated risk score.
    
     if result["status"] not in ["verified", "clear"]:
        risk_score += 40
          
    # -------------------------
    # Loan amount rule
    # -------------------------

    if state["loan_amount"] > 500000:
        risk_score += 40

    # -------------------------
    # Determine risk category
    # -------------------------

    if risk_score < 30:
        risk_category = "low"
    elif risk_score < 60:
        risk_category = "medium"
    else:
        risk_category = "high"

    print(
        f"Risk assessment completed: "
        f"score={risk_score}, "
        f"category={risk_category}"
    )

    return {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "current_stage": "risk_assessed",
        "status": "risk_assessment_complete",
    }

def check_policy(state: LoanState) -> dict:
    """
    Perform a simulated policy check.

    This node evaluates the risk assessment
    against simple workflow rules.

    These are demonstration rules only and
    do not represent an actual lending policy.
    """

    application_id = state["application_id"]
    risk_category = state["risk_category"]

    print(
        f"Checking policy for: "
        f"{application_id}"
    )

    if risk_category == "low":

        policy_status = "eligible_for_next_stage"

        policy_reason = (
            "Application passed the simulated "
            "risk policy checks."
        )

    else:

        policy_status = "requires_human_review"

        policy_reason = (
            "Application requires additional "
            "human review under the simulated policy."
        )

    print(
        f"Policy result: "
        f"{policy_status}"
    )

    return {
        "policy_status": policy_status,
        "policy_reason": policy_reason,
        "current_stage": "policy_checked",
        "status": "policy_check_complete",
    }

def decide_after_policy(state: LoanState) -> str:
    """
    Decide where the workflow should go
    after the policy check.
    """

    if state["policy_status"] == "eligible_for_next_stage":
        return "proceed"

    return "human_review"

def human_review(state: LoanState) -> dict:
    """
    Pause the workflow and request a human decision.

    The workflow can be resumed later with
    the human's response.
    """

    application_id = state["application_id"]

    print(
        f"Human review required for: "
        f"{application_id}"
    )

    decision = interrupt(
        {
            "message": "Human review required.",
            "application_id": application_id,
            "risk_score": state["risk_score"],
            "risk_category": state["risk_category"],
            "policy_reason": state["policy_reason"],
        }
    )

    return {
        "human_decision": decision,
        "current_stage": "human_review_completed",
        "status": "human_decision_received",
    }

def decide_after_human_review(state: LoanState) -> str:
    """
    Route the workflow based on the human's decision.
    """

    if state["human_decision"] == "approve":
        return "proceed"

    return "reject"

def finalize_application(state: LoanState) -> dict:
    """
    Finalize the workflow after a human decision.
    """

    decision = state["human_decision"]

    if decision == "approve":

        print(
            f"Human decision received: "
            f"APPROVE"
        )

        return {
            "current_stage": "application_finalized",
            "status": "approved_for_next_stage",
        }

    print(
        f"Human decision received: "
        f"REJECT"
    )

    return {
        "current_stage": "application_finalized",
        "status": "rejected_after_human_review",
    }
