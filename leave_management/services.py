from datetime import timedelta
from decimal import Decimal
from .models import LeaveBalance, LeaveRequest

def calculate_leave_days(start_date, end_date, leave_span, enable_sandwich):
    """
    Computes total days based on spans and sandwich rules.
    """
    if leave_span in ['FIRST_HALF', 'SECOND_HALF']:
        return Decimal('0.5'), Decimal('0.0')

    total_days = (end_date - start_date).days + 1
    sandwiched_count = 0

    if enable_sandwich:
        curr = start_date
        while curr <= end_date:
            # If weekend (Saturday=5, Sunday=6) falls inside the requested span
            if curr.weekday() in [5, 6]:
                sandwiched_count += 1
            curr += timedelta(days=1)

    return Decimal(str(total_days)), Decimal(str(sandwiched_count))

def update_balance_for_request(request_obj, action):
    """
    Safely adjusts leave balances depending on workflow transitions.
    """
    year = request_obj.start_date.year
    balance, _ = LeaveBalance.objects.get_or_create(
        employee=request_obj.employee,
        leave_type=request_obj.leave_type,
        year=year
    )

    days = request_obj.calculated_days

    if action == 'SUBMIT':
        balance.pending += days
    elif action == 'APPROVE':
        balance.pending -= days
        balance.used += days
    elif action == 'REJECT':
        balance.pending -= days
    elif action == 'CANCEL':
        balance.used -= days

    balance.save()