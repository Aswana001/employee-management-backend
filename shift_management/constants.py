# System State Machine Configuration Tokens
ASSIGNMENT_TYPES = [
    ('Permanent', 'Permanent Structural Shift'),
    ('Temporary', 'Temporary Coverage Shift'),
    ('Weekly', 'Weekly Schedule Variant'),
]

ASSIGNMENT_STATUS = [
    ('Active', 'Currently Operational'),
    ('Expired', 'Past Effective Window'),
]

ROTATION_TYPES = [
    ('Morning -> Evening', 'Morning to Evening Transition'),
    ('Evening -> Night', 'Evening to Night Transition'),
    ('Weekly Rotation', 'Cycles Weekly'),
    ('Monthly Rotation', 'Cycles Monthly'),
]

SWAP_STATUS = [
    ('Pending', 'Awaiting Verification Review'),
    ('Approved', 'Formally Executed and Completed'),
    ('Rejected', 'Denied by Processing Authority'),
    ('Cancelled', 'Retracted by Originating Staff'),
]
