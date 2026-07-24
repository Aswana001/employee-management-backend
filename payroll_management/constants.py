BATCH_STATUS_CHOICES = [
    ('DRAFT', 'Draft Computation'),
    ('PROCESSED', 'Processed & Pending Review'),
    ('APPROVED', 'Approved by HR'),
    ('PAID', 'Disbursed to Bank'),
]

COMPONENT_TYPE_CHOICES = [
    ('BONUS', 'Performance Bonus'),
    ('INCENTIVE', 'Sales Incentive'),
    ('ARREARS', 'Back-Pay Arrears'),
    ('REIMBURSEMENT', 'Tax-Free Reimbursement'),
]

SETTLEMENT_STATUS_CHOICES = [
    ('PENDING', 'Pending HR Review'),
    ('APPROVED', 'Approved for Final Payout'),
    ('PAID', 'Settlement Disbursed'),
]