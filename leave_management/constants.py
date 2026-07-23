LEAVE_SPAN_CHOICES = [
    ('FULL_DAY', 'Full Day'),
    ('FIRST_HALF', 'Half Day - First Half'),
    ('SECOND_HALF', 'Half Day - Second Half'),
]

APPROVAL_STATUS_CHOICES = [
    ('PENDING_L1', 'Pending Level 1 Manager Review'),
    ('PENDING_L2', 'Pending Level 2 HR Review'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('CANCEL_REQUESTED', 'Cancellation Requested'),
    ('CANCELLED', 'Cancelled'),
]

COMP_OFF_STATUS_CHOICES = [
    ('PENDING', 'Pending HR Review'),
    ('APPROVED', 'Approved and Credited'),
    ('REJECTED', 'Rejected'),
]

ENCASHMENT_STATUS_CHOICES = [
    ('PENDING', 'Pending HR Review'),
    ('APPROVED', 'Approved for Payroll'),
    ('REJECTED', 'Rejected'),
]