import tempfile, unittest
from pathlib import Path
from app import ExpenseStore
class StoreTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.store=ExpenseStore(Path(self.temp.name)/"test.db")
 def tearDown(self): self.temp.cleanup()
 def test_add_list(self):
  self.store.add("2026-10-22","Food",120,"Lunch")
  self.assertEqual(self.store.list_expenses()[0]["description"],"Lunch")
 def test_month_filter(self):
  self.store.add("2026-10-01","Food",100,"Meal"); self.store.add("2026-09-01","Bus",50,"Travel")
  self.assertEqual(len(self.store.list_expenses("2026-10")),1)
 def test_summary(self):
  self.store.add("2026-10-01","Food",100,"Meal")
  self.assertEqual(self.store.summary("2026-10")[:2],(100.0,1))
 def test_delete(self):
  self.store.add("2026-10-01","Food",100,"Meal"); self.store.delete(self.store.list_expenses()[0]["id"])
  self.assertEqual(len(self.store.list_expenses()),0)
if __name__=="__main__": unittest.main()
