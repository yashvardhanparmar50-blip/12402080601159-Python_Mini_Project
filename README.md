# SpendWise — Student Expense Tracker (Dark Modern GUI)

## Features
- Dark dashboard with summary cards (total, count, average)
- Add expenses with date, category, amount and description
- Local SQLite database (`expenses.db`, created automatically)
- Filter by month/category and search by category/description
- View details, delete selected expenses, export matching rows to CSV
- Standard-library-only Python app (Tkinter + SQLite)

## Run on Windows
1. Extract this ZIP.
2. Open the extracted `Student_Expense_Tracker_Modern` folder.
3. Click the File Explorer address bar, type `cmd`, press Enter.
4. Run `python app.py` (or `py app.py`).

On macOS/Linux, run `python3 app.py`.

Python 3.10+ recommended. Tkinter is normally included with Python on Windows.
Your data is stored beside `app.py` in `expenses.db`; keep this file to preserve records.
