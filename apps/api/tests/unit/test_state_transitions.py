from app.domain.enums import PrescriptionStatus, PlanState, JobState
from app.domain.state_transitions import (
    can_transition_prescription,
    can_transition_plan,
    can_transition_job,
)


def test_prescription_transitions():
    assert can_transition_prescription(PrescriptionStatus.DRAFT, PrescriptionStatus.EXTRACTING)
    assert can_transition_prescription(PrescriptionStatus.EXTRACTING, PrescriptionStatus.NEEDS_CONFIRMATION)
    assert can_transition_prescription(PrescriptionStatus.NEEDS_CONFIRMATION, PrescriptionStatus.CONFIRMED)
    assert can_transition_prescription(PrescriptionStatus.CONFIRMED, PrescriptionStatus.COMPLETED)
    assert can_transition_prescription(PrescriptionStatus.CONFIRMED, PrescriptionStatus.NEEDS_CONFIRMATION)  # Edit invalidation

    # Immutable completed state
    assert not can_transition_prescription(PrescriptionStatus.COMPLETED, PrescriptionStatus.DRAFT)
    assert not can_transition_prescription(PrescriptionStatus.COMPLETED, PrescriptionStatus.CANCELLED)


def test_plan_transitions():
    assert can_transition_plan(PlanState.DRAFT, PlanState.PENDING_REVIEW)
    assert can_transition_plan(PlanState.PENDING_REVIEW, PlanState.APPROVED)
    assert can_transition_plan(PlanState.PENDING_REVIEW, PlanState.REJECTED)
    assert can_transition_plan(PlanState.APPROVED, PlanState.FINALIZED)
    assert can_transition_plan(PlanState.APPROVED, PlanState.PENDING_REVIEW)  # Invalidated by quote expiry or stock change

    assert not can_transition_plan(PlanState.FINALIZED, PlanState.APPROVED)


def test_job_transitions():
    assert can_transition_job(JobState.QUEUED, JobState.RUNNING)
    assert can_transition_job(JobState.RUNNING, JobState.SUCCEEDED)
    assert can_transition_job(JobState.RUNNING, JobState.FAILED)
    assert can_transition_job(JobState.RUNNING, JobState.QUEUED)  # Bounded retry / lease recovery
