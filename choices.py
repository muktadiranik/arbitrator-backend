import constants

CATEGORY_CHOICES = [
    (constants.GENERAL_CONTRACTOR, "General Contractor"),
]

TYPE_CHOICES = [
    (constants.ARBITRATOR, 'Arbitrator'),
    (constants.CLAIMER, 'Claimer'),
    (constants.CREATOR, 'Creator'),
    (constants.WITNESS, 'Witness'),
    (constants.RESPONDENT, 'Respondent')
]

ACCOUNT_CHOICES = [
    (constants.INDIVIDUAL, 'individual'),
    (constants.ORGANIZATION, 'organization')
]
STATUS_CHOICES = [
    (constants.IN_PROGRESS, 'in-progress'),
    (constants.RESOLVED, 'resolved'),
    (constants.UNRESOLVED, 'unresolved'),
    (constants.WAITING_FOR_SIGNUP, 'waiting-for-sign-up')
]

DISPUTE_TYPE_CHOICES = [
    (constants.HEARING, 'hearing')
]

OFFER_CHOICES = [
    (constants.PENDING, 'pending'),
    (constants.COUNTER_OFFER, 'counter-offer'),
    (constants.REJECTED, 'rejected'),
    (constants.ACCEPTED, 'accepted')
]

INVITATION_STATUS_CHOICES = [
    (constants.INVITATION_STATUS_SENT, 'sent'),
    (constants.INVITATION_STATUS_DRAFT, 'draft'),
    (constants.INVITATION_STATUS_PENDING, 'pending'),
    (constants.INVITATION_STATUS_SIGNED, 'signed')
]

LIBRARY_CHOICES = [
    (constants.LIBRARY_CHOICE_GLOBAL, 'global'),
    (constants.LIBRARY_CHOICE_TRAINING, 'training')
]

LIBRARY_FOLDER_CHOICES = [
    (constants.ROOT_FOLDER, 'root'),
    (constants.CHILD_FOLDER, 'child')
]

TIME_LOG_TYPE_CHOICES = [
    (constants.TYPE_CAUCUS, 'Caucus'),
    (constants.TYPE_PLENARY, 'Plenary'),
    (constants.TYPE_GENERAL, 'General')
]

DISPUTE_USER_ACTIONS = [
    (constants.APPROVAL_ACTION, 'Approve'),
    (constants.STRAIGHT_TO_HEARING_ACTION, 'Straight to hearing')
]

DISPUTE_USER_ACTIONS_VALUES = [
    (constants.DISPUTE_USER_ACTION_ACCEPTED, 'Accept'),
    (constants.DISPUTE_USER_ACTION_REJECTED, 'Reject'),
    (constants.DISPUTE_USER_ACTION_PENDING, 'Pending')
]

CURRENCY_CHOICES = [
    (constants.CURRENCY_USD, 'USD'),
    (constants.CURRENCY_EUR, 'EUR'),
    (constants.CURRENCY_JPY, 'JPY')
]

JOB_TYPE_CHOICES = [
    (constants.JOB_TYPE_REMOTE, "Remote Work"),
    (constants.JOB_TYPE_ON_SITE, "On-site Work")
]

EMPLOYMENT_TYPE_CHOICES = [
    (constants.EMPLOYMENT_TYPE_FULL_TIME_EMPLOYEE, 'Full-time employee'),
    (constants.EMPLOYMENT_TYPE_INDEPENDENT_CONTRACTOR, 'Independent contractor')
]

JOB_DETAILS_TYPE_CHOICES = (
    (constants.JOB_DETAIL_REQUIREMENT, 'Requirement'),
    (constants.JOB_DETAIL_OPPORTUNITY, 'Opportunity')
)

PAYMENT_STATUS_CHOICES = (
    (constants.PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD, 'requires_payment_method'),
    (constants.PAYMENT_STATUS_REQUIRES_CONFIRMATION, 'requires_confirmation'),
    (constants.PAYMENT_STATUS_REQUIRES_ACTION, 'requires_action'),
    (constants.PAYMENT_STATUS_PROCESSING, 'processing'),
    (constants.PAYMENT_STATUS_REQUIRES_CAPTURE, 'requires_capture'),
    (constants.PAYMENT_STATUS_SUCCEEDED, 'succeeded'),
    (constants.PAYMENT_STATUS_CANCELED, 'canceled'),
    (constants.PAYMENT_STATUS_FAILED, 'failed'),
    (constants.PAYMENT_STATUS_EXPIRED, 'expired'),
    (constants.PAYMENT_STATUS_VOID, 'void')
)
