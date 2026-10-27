"""SpendWise dark modern Student Expense Tracker. Run with: python app.py"""
import csv, sqlite3, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"
BG="#0b1120"; PANEL="#111a2e"; PANEL_ALT="#16223a"; BORDER="#25334f"
TEXT="#e8eefb"; MUTED="#92a2bf"; ACCENT="#6d7cff"; ACCENT_HOVER="#8591ff"
GREEN="#38d39f"; RED="#ff6b81"; GOLD="#f5c66b"; INPUT="#0d1628"

class ExpenseStore:
    """SQLite persistence layer."""
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path); self._create_table()
    def _connect(self):
        con=sqlite3.connect(self.db_path); con.row_factory=sqlite3.Row; return con
    def _create_table(self):
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spent_on TEXT NOT NULL, category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0), description TEXT NOT NULL)""")
    def add(self, spent_on, category, amount, description):
        with self._connect() as con:
            con.execute("INSERT INTO expenses(spent_on,category,amount,description) VALUES(?,?,?,?)",
                        (spent_on,category,amount,description.strip()))
    def delete(self, expense_id):
        with self._connect() as con: con.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    def list_expenses(self, month="All months", category="All categories", search=""):
        sql="SELECT id,spent_on,category,amount,description FROM expenses WHERE 1=1"; args=[]
        if month!="All months": sql+=" AND substr(spent_on,1,7)=?"; args.append(month)
        if category!="All categories": sql+=" AND category=?"; args.append(category)
        if search.strip():
            sql+=" AND (lower(description) LIKE ? OR lower(category) LIKE ?)"
            term=f"%{search.strip().lower()}%"; args.extend([term,term])
        sql+=" ORDER BY spent_on DESC,id DESC"
        with self._connect() as con: return con.execute(sql,args).fetchall()
    def categories(self):
        with self._connect() as con:
            return [r["category"] for r in con.execute("SELECT DISTINCT category FROM expenses ORDER BY category")]
    def months(self):
        with self._connect() as con:
            return [r["month"] for r in con.execute("SELECT DISTINCT substr(spent_on,1,7) month FROM expenses ORDER BY month DESC")]
    def summary(self, month="All months"):
        where=""; args=[]
        if month!="All months": where=" WHERE substr(spent_on,1,7)=?"; args.append(month)
        with self._connect() as con:
            total=con.execute("SELECT COALESCE(SUM(amount),0) total FROM expenses"+where,args).fetchone()["total"]
            count=con.execute("SELECT COUNT(*) count FROM expenses"+where,args).fetchone()["count"]
            cats=con.execute("SELECT category,SUM(amount) total FROM expenses"+where+" GROUP BY category ORDER BY total DESC LIMIT 5",args).fetchall()
        return float(total),int(count),cats
    def export_csv(self,path,rows):
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f); w.writerow(["ID","Date","Category","Amount (INR)","Description"])
            for r in rows: w.writerow([r["id"],r["spent_on"],r["category"],f'{r["amount"]:.2f}',r["description"]])

class ExpenseTrackerApp:
    def __init__(self,root):
        self.root=root; self.store=ExpenseStore()
        root.title("SpendWise | Student Expense Tracker"); root.geometry("1180x760")
        root.minsize(1000,660); root.configure(bg=BG)
        self.month_var=tk.StringVar(value="All months"); self.cat_filter=tk.StringVar(value="All categories")
        self.search_var=tk.StringVar(); self.date_var=tk.StringVar(value=date.today().isoformat())
        self.category_var=tk.StringVar(value="Food"); self.amount_var=tk.StringVar(); self.desc_var=tk.StringVar()
        self._styles(); self._build(); self.refresh()
    def _styles(self):
        s=ttk.Style(); s.theme_use("clam")
        s.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=TEXT,rowheight=36,borderwidth=0,font=("Segoe UI",10))
        s.configure("Treeview.Heading",background=PANEL_ALT,foreground=MUTED,font=("Segoe UI",9,"bold"),relief="flat",padding=(10,12))
        s.map("Treeview",background=[("selected","#2a3960")],foreground=[("selected","#ffffff")])
        s.configure("TCombobox",fieldbackground=INPUT,background=PANEL_ALT,foreground=TEXT,arrowcolor=TEXT)
        s.map("TCombobox",fieldbackground=[("readonly",INPUT)],foreground=[("readonly",TEXT)])
        s.configure("Vertical.TScrollbar",background=PANEL_ALT,troughcolor=BG,bordercolor=BG,arrowcolor=MUTED)
    def _label(self,parent,text,color=MUTED,size=10,bold=False):
        return tk.Label(parent,text=text,bg=parent.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))
    def _panel(self,parent,**kw):
        return tk.Frame(parent,bg=PANEL,highlightthickness=1,highlightbackground=BORDER,**kw)
    def _button(self,parent,text,command,primary=False,danger=False):
        color=RED if danger else (ACCENT if primary else PANEL_ALT)
        hover="#ff8798" if danger else (ACCENT_HOVER if primary else "#20304e")
        b=tk.Button(parent,text=text,command=command,bg=color,fg="#ffffff" if primary or danger else TEXT,
            activebackground=hover,activeforeground="#ffffff",relief="flat",bd=0,padx=14,pady=10,
            cursor="hand2",font=("Segoe UI",10,"bold"))
        b.bind("<Enter>",lambda _e:b.configure(bg=hover)); b.bind("<Leave>",lambda _e:b.configure(bg=color))
        return b
    def _entry(self,parent,var):
        return tk.Entry(parent,textvariable=var,bg=INPUT,fg=TEXT,insertbackground=TEXT,relief="flat",
            highlightthickness=1,highlightbackground=BORDER,highlightcolor=ACCENT,font=("Segoe UI",10))
    def _build(self):
        header=tk.Frame(self.root,bg=BG); header.pack(fill="x",padx=28,pady=(22,18))
        left=tk.Frame(header,bg=BG); left.pack(side="left")
        tk.Label(left,text="SpendWise",bg=BG,fg=TEXT,font=("Segoe UI",23,"bold")).pack(anchor="w")
        tk.Label(left,text="STUDENT EXPENSE TRACKER  •  PERSONAL FINANCE, MADE SIMPLE",
                 bg=BG,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(3,0))
        self._button(header,"＋  Add expense",self.focus_amount,primary=True).pack(side="right")
        cards=tk.Frame(self.root,bg=BG); cards.pack(fill="x",padx=28,pady=(0,18))
        for i in range(3): cards.grid_columnconfigure(i,weight=1,uniform="card")
        self.total=self._card(cards,0,"TOTAL SPENDING","₹0.00",ACCENT)
        self.count=self._card(cards,1,"RECORDED EXPENSES","0",GREEN)
        self.average=self._card(cards,2,"AVERAGE PER EXPENSE","₹0.00",GOLD)
        body=tk.Frame(self.root,bg=BG); body.pack(fill="both",expand=True,padx=28,pady=(0,22))
        body.grid_columnconfigure(0,weight=0,minsize=305); body.grid_columnconfigure(1,weight=1); body.grid_rowconfigure(0,weight=1)
        form=self._panel(body,padx=20,pady=18); form.grid(row=0,column=0,sticky="nsew",padx=(0,16))
        tk.Label(form,text="Add an expense",bg=PANEL,fg=TEXT,font=("Segoe UI",15,"bold")).pack(anchor="w")
        tk.Label(form,text="Enter the details below to log a purchase.",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",pady=(5,18))
        self._label(form,"DATE  •  YYYY-MM-DD",size=9,bold=True).pack(anchor="w",pady=(0,7))
        self._entry(form,self.date_var).pack(fill="x",ipady=9,pady=(0,14))
        self._label(form,"CATEGORY",size=9,bold=True).pack(anchor="w",pady=(0,7))
        self.cat_combo=ttk.Combobox(form,textvariable=self.category_var,values=["Food","Transport","Education","Shopping","Bills","Health","Entertainment","Other"])
        self.cat_combo.pack(fill="x",ipady=5,pady=(0,14))
        self._label(form,"AMOUNT (₹)",size=9,bold=True).pack(anchor="w",pady=(0,7))
        self.amount_entry=self._entry(form,self.amount_var); self.amount_entry.pack(fill="x",ipady=9,pady=(0,14))
        self.amount_entry.bind("<Return>",lambda _e:self.add_expense())
        self._label(form,"DESCRIPTION",size=9,bold=True).pack(anchor="w",pady=(0,7))
        self._entry(form,self.desc_var).pack(fill="x",ipady=9,pady=(0,18))
        self._button(form,"Save expense",self.add_expense,primary=True).pack(fill="x")
        self._button(form,"Clear form",self.clear_form).pack(fill="x",pady=(9,0))
        tk.Label(form,text="Your data stays on this computer.",bg=PANEL,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",side="bottom",pady=(20,0))
        records=self._panel(body,padx=18,pady=16); records.grid(row=0,column=1,sticky="nsew")
        records.grid_rowconfigure(2,weight=1); records.grid_columnconfigure(0,weight=1)
        top=tk.Frame(records,bg=PANEL); top.grid(row=0,column=0,sticky="ew")
        tk.Label(top,text="Recent transactions",bg=PANEL,fg=TEXT,font=("Segoe UI",15,"bold")).pack(side="left")
        self._button(top,"Export CSV",self.export_csv).pack(side="right")
        filters=tk.Frame(records,bg=PANEL); filters.grid(row=1,column=0,sticky="ew",pady=(16,12))
        self.month_combo=ttk.Combobox(filters,textvariable=self.month_var,state="readonly",width=13)
        self.month_combo.pack(side="left",padx=(0,8)); self.month_combo.bind("<<ComboboxSelected>>",lambda _e:self.refresh())
        self.cat_filter_combo=ttk.Combobox(filters,textvariable=self.cat_filter,state="readonly",width=15)
        self.cat_filter_combo.pack(side="left",padx=(0,8)); self.cat_filter_combo.bind("<<ComboboxSelected>>",lambda _e:self.refresh())
        search_wrap=tk.Frame(filters,bg=INPUT,highlightthickness=1,highlightbackground=BORDER); search_wrap.pack(side="left",fill="x",expand=True)
        tk.Label(search_wrap,text="⌕",bg=INPUT,fg=MUTED,font=("Segoe UI",13)).pack(side="left",padx=(9,2))
        self._entry(search_wrap,self.search_var).pack(side="left",fill="x",expand=True,ipady=7,padx=(0,8))
        self.search_var.trace_add("write",lambda *_:self.refresh())
        table=tk.Frame(records,bg=PANEL); table.grid(row=2,column=0,sticky="nsew"); table.grid_rowconfigure(0,weight=1); table.grid_columnconfigure(0,weight=1)
        cols=("date","category","description","amount")
        self.tree=ttk.Treeview(table,columns=cols,show="headings",selectmode="browse")
        for col,title,width,anchor in [("date","DATE",100,"w"),("category","CATEGORY",120,"w"),("description","DESCRIPTION",220,"w"),("amount","AMOUNT",110,"e")]:
            self.tree.heading(col,text=title); self.tree.column(col,width=width,anchor=anchor,stretch=(col=="description"))
        scroll=ttk.Scrollbar(table,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0,column=0,sticky="nsew"); scroll.grid(row=0,column=1,sticky="ns")
        self.tree.bind("<Double-1>",lambda _e:self.show_selected())
        bottom=tk.Frame(records,bg=PANEL); bottom.grid(row=3,column=0,sticky="ew",pady=(12,0))
        self.status=tk.Label(bottom,text="Ready",bg=PANEL,fg=MUTED,font=("Segoe UI",9)); self.status.pack(side="left")
        self._button(bottom,"View details",self.show_selected).pack(side="right",padx=(8,0))
        self._button(bottom,"Delete selected",self.delete_selected,danger=True).pack(side="right")
    def _card(self,parent,col,heading,value,accent):
        card=self._panel(parent,padx=18,pady=15)
        card.grid(row=0,column=col,sticky="ew",padx=(0 if col==0 else 7,7 if col<2 else 0))
        tk.Label(card,text=heading,bg=PANEL,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w")
        val=tk.Label(card,text=value,bg=PANEL,fg=TEXT,font=("Segoe UI",22,"bold")); val.pack(anchor="w",pady=(8,0))
        tk.Frame(card,bg=accent,height=3).pack(fill="x",side="bottom",pady=(14,0)); return val
    def focus_amount(self): self.amount_entry.focus_set()
    def clear_form(self):
        self.date_var.set(date.today().isoformat()); self.category_var.set("Food"); self.amount_var.set(""); self.desc_var.set(""); self.amount_entry.focus_set()
    def add_expense(self):
        d=self.date_var.get().strip(); category=self.category_var.get().strip(); desc=self.desc_var.get().strip()
        try:
            parsed=datetime.strptime(d,"%Y-%m-%d").date()
            if parsed.isoformat()!=d: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid date","Enter date as YYYY-MM-DD, for example 2026-10-22."); return
        try:
            amount=float(self.amount_var.get().strip())
            if amount<=0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount","Enter an amount greater than ₹0."); return
        if not category: messagebox.showerror("Missing category","Select or enter a category."); return
        if not desc: messagebox.showerror("Missing description","Enter a short description."); return
        try: self.store.add(d,category,amount,desc)
        except sqlite3.Error as exc: messagebox.showerror("Database error",f"Could not save expense.\n\n{exc}"); return
        self.clear_form(); self.month_var.set("All months"); self.cat_filter.set("All categories"); self.search_var.set("")
        self.refresh(); self.status.configure(text="Expense saved successfully.",fg=GREEN)
    def refresh(self):
        months=["All months"]+self.store.months(); self.month_combo.configure(values=months)
        if self.month_var.get() not in months: self.month_var.set("All months")
        cats=["All categories"]+self.store.categories(); self.cat_filter_combo.configure(values=cats)
        if self.cat_filter.get() not in cats: self.cat_filter.set("All categories")
        rows=self.store.list_expenses(self.month_var.get(),self.cat_filter.get(),self.search_var.get())
        for item in self.tree.get_children(): self.tree.delete(item)
        for r in rows:
            self.tree.insert("","end",iid=str(r["id"]),values=(r["spent_on"],r["category"],r["description"],f'₹{r["amount"]:,.2f}'))
        total,count,_=self.store.summary(self.month_var.get())
        self.total.configure(text=f"₹{total:,.2f}"); self.count.configure(text=str(count))
        self.average.configure(text=f"₹{total/count:,.2f}" if count else "₹0.00")
        self.status.configure(text=f"Showing {len(rows)} matching transaction(s)" if rows else "No transactions match these filters.",fg=MUTED)
    def selected_id(self):
        sel=self.tree.selection()
        if not sel: messagebox.showinfo("Select a transaction","Choose a transaction from the table first."); return None
        return sel[0]
    def show_selected(self):
        rid=self.selected_id()
        if rid is None:return
        v=self.tree.item(rid,"values")
        messagebox.showinfo("Expense details",f"Date: {v[0]}\nCategory: {v[1]}\nDescription: {v[2]}\nAmount: {v[3]}")
    def delete_selected(self):
        rid=self.selected_id()
        if rid is None:return
        v=self.tree.item(rid,"values")
        if not messagebox.askyesno("Delete expense",f"Delete this expense?\n\n{v[0]} • {v[1]} • {v[3]}"):return
        try:self.store.delete(int(rid))
        except sqlite3.Error as exc:messagebox.showerror("Database error",f"Could not delete expense.\n\n{exc}");return
        self.refresh(); self.status.configure(text="Expense deleted.",fg=GREEN)
    def export_csv(self):
        rows=self.store.list_expenses(self.month_var.get(),self.cat_filter.get(),self.search_var.get())
        if not rows:messagebox.showinfo("Nothing to export","There are no matching transactions to export.");return
        path=filedialog.asksaveasfilename(title="Export expenses",defaultextension=".csv",filetypes=[("CSV files","*.csv")],initialfile="student_expenses.csv")
        if not path:return
        try:self.store.export_csv(path,rows)
        except OSError as exc:messagebox.showerror("Export failed",f"Could not export CSV.\n\n{exc}");return
        messagebox.showinfo("Export complete",f"Exported {len(rows)} transaction(s) to:\n{path}")

def main():
    root=tk.Tk(); ExpenseTrackerApp(root); root.mainloop()
if __name__=="__main__": main()
