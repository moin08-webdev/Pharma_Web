from app.domain.enums import PrescriptionStatus, PlanState, JobState


VALID_PRESCRIPTION_TRANSITIONS = {
    PrescriptionStatus.DRAFT: {
        PrescriptionStatus.EXTRACTING,
        PrescriptionStatus.NEEDS_CONFIRMATION,
        PrescriptionStatus.CANCELLED,
    },
    PrescriptionStatus.EXTRACTING: {
        PrescriptionStatus.NEEDS_CONFIRMATION,
        PrescriptionStatus.CANCELLED,
    },
    PrescriptionStatus.NEEDS_CONFIRMATION: {
        PrescriptionStatus.CONFIRMED,
        PrescriptionStatus.CANCELLED,
    },
    PrescriptionStatus.CONFIRMED: {
        PrescriptionStatus.NEEDS_CONFIRMATION,
        PrescriptionStatus.COMPLETED,
        PrescriptionStatus.CANCELLED,
    },
    PrescriptionStatus.COMPLETED: set(),  # Immutable terminal state
    PrescriptionStatus.CANCELLED: set(),  # Terminal state
}

VALID_PLAN_TRANSITIONS = {
    PlanState.DRAFT: {
        PlanState.PENDING_REVIEW,
        PlanState.SUPERSEDED,
    },
    PlanState.PENDING_REVIEW: {
        PlanState.APPROVED,
        PlanState.REJECTED,
        PlanState.SUPERSEDED,
    },
    PlanState.APPROVED: {
        PlanState.FINALIZED,
        PlanState.PENDING_REVIEW,  # If invalidated by edits/stale quote
        PlanState.SUPERSEDED,
    },
    PlanState.REJECTED: {
        PlanState.PENDING_REVIEW,  # Re-submitted with adjustments
        PlanState.SUPERSEDED,
    },
    PlanState.SUPERSEDED: set(),  # Terminal
    PlanState.FINALIZED: set(),   # Terminal
}

VALID_JOB_TRANSITIONS = {
    JobState.QUEUED: {JobState.RUNNING},
    JobState.RUNNING: {JobState.SUCCEEDED, JobState.FAILED, JobState.QUEUED},
    JobState.SUCCEEDED: set(),
    JobState.FAILED: {JobState.QUEUED},  # For manual retry or bounded retry
}


def can_transition_prescription(current: PrescriptionStatus, target: PrescriptionStatus) -> bool:
    return target in VALID_PRESCRIPTION_TRANSITIONS.get(current, set())


def can_transition_plan(current: PlanState, target: PlanState) -> bool:
    return target in VALID_PLAN_TRANSITIONS.get(current, set())


def can_transition_job(current: JobState, target: JobState) -> bool:
    return target in VALID_JOB_TRANSITIONS.get(current, set())
