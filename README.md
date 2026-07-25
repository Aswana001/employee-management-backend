# 📡 Complete HRMS API Endpoints Reference

Base URL: `http://127.0.0.1:8000/api/v1/`

---

## 💵 1. Payroll Management Module (`/api/v1/payroll/`)

| Method | API Endpoint | Description / Function |
| :--- | :--- | :--- |
| `POST` / `GET` | `/api/v1/payroll/structures/` | Define/assign or list employee salary structures (Basic, HRA, PF, ESI, TDS). |
| `GET` / `PUT` | `/api/v1/payroll/structures/<employee_id>/` | View or update the salary structure of a specific employee. |
| `POST` / `GET` | `/api/v1/payroll/components/` | Add or list variable earnings (Bonuses, Sales Incentives, Back-Pay Arrears). |
| `POST` | `/api/v1/payroll/generate/` | Batch calculates monthly payroll for all active employees for a target month/year. |
| `POST` | `/api/v1/payroll/batches/<id>/lock/` | Lock a processed batch and mark status as PAID. |
| `GET` | `/api/v1/payroll/payslip/<employee_id>/<month>/<year>/` | Fetch a detailed individual monthly payslip breakdown. |
| `GET` | `/api/v1/payroll/reports/summary/?month=<M>&year=<Y>` | Get aggregate financial reporting (Total Gross, Total PF/TDS, Net Bank Payout). |
| `POST` | `/api/v1/payroll/settlement/` | Process Full & Final (F&F) Settlement for departing staff. |

---

## 🌴 2. Leave Management Module (`/api/v1/leaves/`)

| Method | API Endpoint | Description / Function |
| :--- | :--- | :--- |
| `POST` / `GET` | `/api/v1/leaves/types/` | Configure leave types (Casual, Sick, Comp-Off) and sandwich policies. |
| `GET` | `/api/v1/leaves/balance/<employee_id>/` | Fetch allocated, used, pending, and remaining leave balances. |
| `POST` | `/api/v1/leaves/apply/` | Submit a leave application (Supports Full Day, Half Day, and Sandwich checks). |
| `POST` | `/api/v1/leaves/<id>/approve/` | Multi-level approval handler (Level 1 Manager -> Level 2 HR -> Approved). |
| `POST` | `/api/v1/leaves/<id>/reject/` | Reject a leave application with a reason (Releases pending balance). |
| `POST` | `/api/v1/leaves/<id>/cancel/` | Cancel leave request (Refunds used balance back if previously approved). |
| `POST` / `GET` | `/api/v1/leaves/comp-off/claim/` | Submit or list claims for working on weekends/holidays. |
| `POST` | `/api/v1/leaves/comp-off/<id>/approve/` | Approve comp-off claim, crediting +1.0 day to the employee's balance. |
| `POST` | `/api/v1/leaves/encash/` | Request to encash unused leave balances. |

---

## ⏰ 3. Shift Management Module (`/api/v1/shifts/` or as mapped)

| Method | API Endpoint | Description / Function |
| :--- | :--- | :--- |
| `POST` / `GET` | `/api/v1/shifts/` | List all shifts or create new shift rules (Detects Night Shifts automatically). |
| `GET` / `PUT` / `DELETE` | `/api/v1/shifts/<id>/` | Retrieve, update, or remove a shift configuration. |
| `POST` / `GET` | `/api/v1/assignments/` | Assign employees to shifts (Enforces timeline collision/overlap validation). |
| `GET` | `/api/v1/assignments/active/<employee_id>/` | Fetch the active scheduled shift for an employee for today. |
| `POST` / `GET` | `/api/v1/schedules/weekly/` | Set up weekly schedule matrix per employee. |
| `POST` / `GET` | `/api/v1/rotations/` | Set up alternating shift rotation schedules. |
| `POST` | `/api/v1/swaps/request/` | Employee initiates a shift swap request with a peer. |
| `POST` | `/api/v1/swaps/<id>/<action>/` | Manager workflow action (approve or reject shift trade). |
| `POST` / `GET` | `/api/v1/holidays/` | Assign and track holiday shift schedules with multipliers. |
| `GET` | `/api/v1/overtime/calculate/<employee_id>/` | Calculate net compensable overtime hours and pay rates. |