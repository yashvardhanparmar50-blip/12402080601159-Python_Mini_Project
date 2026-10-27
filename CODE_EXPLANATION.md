# Code Walkthrough — SpendWise

- `ExpenseStore` is the data layer. It creates the SQLite table and provides add, delete, list, summary and CSV export operations.
- `ExpenseTrackerApp` is the GUI layer. It builds the dark dashboard, summary cards, expense form, filter controls, search box and transaction table.
- `add_expense()` validates date format, positive numeric amount, category and description before inserting a record.
- SQL uses `?` parameter placeholders to safely pass values.
- `refresh()` reloads the transaction table and updates the summary cards.
- `Treeview` presents rows; buttons call functions such as save, delete, view details and export.
- `mainloop()` keeps the Tkinter window responsive to user interaction.
- The app requires no external packages. Data persists in the local `expenses.db` file.
