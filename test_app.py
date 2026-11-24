import unittest
import json
import io
import openpyxl
from datetime import datetime, timedelta
from app import create_app
from database.db import db
from models import User, Account, Transaction, Note, OTPVerification
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DEV_OTP_MODE = True
    SECRET_KEY = "test-secret-key"

class MoneyMateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_01_otp_flow_and_registration(self):
        """Test sending OTP, verifying, and initial account provisioning"""
        # 1. Send OTP
        res = self.client.post("/api/auth/send-otp", json={"phone_number": "9876543210"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("dev_otp", data)
        otp = data["dev_otp"]

        # 2. Verify OTP
        verify_res = self.client.post("/api/auth/verify-otp", json={
            "phone_number": "+919876543210",
            "otp": otp
        })
        self.assertEqual(verify_res.status_code, 200)
        verify_data = verify_res.get_json()
        self.assertTrue(verify_data["success"])

        # Check user and accounts created
        user = User.query.filter_by(phone_number="+919876543210").first()
        self.assertIsNotNone(user)
        accounts = Account.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(accounts), 3)

    def login_test_user(self):
        """Helper to create and login a test user"""
        self.client.post("/api/auth/send-otp", json={"phone_number": "9876543210"})
        otp_rec = OTPVerification.query.order_by(OTPVerification.id.desc()).first()
        # Find raw OTP from last send-otp response or direct verify
        res = self.client.post("/api/auth/send-otp", json={"phone_number": "9999988888"})
        data = res.get_json()
        self.client.post("/api/auth/verify-otp", json={
            "phone_number": data["phone_number"],
            "otp": data["dev_otp"]
        })
        user = User.query.filter_by(phone_number=data["phone_number"]).first()
        return user

    def test_02_account_crud_and_balances(self):
        """Test account creation, update, and balance calculation"""
        user = self.login_test_user()
        
        # List accounts
        res = self.client.get("/api/accounts")
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["accounts"]), 3)
        initial_balance = data["total_balance"]
        self.assertEqual(initial_balance, 28000.00) # 25000 bank + 3000 cash

        # Create new account
        create_res = self.client.post("/api/accounts", json={
            "account_name": "Emergency Fund",
            "account_type": "Bank Account",
            "opening_balance": 10000.00
        })
        self.assertEqual(create_res.status_code, 201)
        new_acc = create_res.get_json()["account"]

        # Check total balance updated
        res = self.client.get("/api/accounts")
        self.assertEqual(res.get_json()["total_balance"], 38000.00)

        # Archive account
        arch_res = self.client.post(f"/api/accounts/{new_acc['id']}/archive")
        self.assertTrue(arch_res.get_json()["success"])

        # Check active accounts list excludes archived by default
        res_active = self.client.get("/api/accounts")
        self.assertEqual(len(res_active.get_json()["accounts"]), 3)

    def test_03_income_and_expense_crud(self):
        """Test adding, editing, and deleting income and expenses"""
        user = self.login_test_user()
        bank_acc = Account.query.filter_by(user_id=user.id, account_type="Bank Account").first()

        # 1. Add Income
        inc_res = self.client.post("/api/transactions", json={
            "transaction_type": "income",
            "amount": 50000.00,
            "category": "Salary",
            "account_id": bank_acc.id,
            "date": "2026-10-01",
            "time": "10:00",
            "description": "Monthly Salary",
            "note": "Software developer"
        })
        self.assertEqual(inc_res.status_code, 201)
        inc_id = inc_res.get_json()["transaction"]["id"]
        
        # Check bank account balance increased
        self.assertEqual(inc_res.get_json()["account_balance"], 75000.00) # 25000 + 50000

        # 2. Add Expense
        exp_res = self.client.post("/api/transactions", json={
            "transaction_type": "expense",
            "amount": 15000.00,
            "category": "Household",
            "account_id": bank_acc.id,
            "date": "2026-10-02",
            "time": "11:00",
            "note": "Rent Payment"
        })
        self.assertEqual(exp_res.status_code, 201)
        exp_id = exp_res.get_json()["transaction"]["id"]
        self.assertEqual(exp_res.get_json()["account_balance"], 60000.00) # 75000 - 15000

        # 3. Update Income
        upd_res = self.client.put(f"/api/transactions/{inc_id}", json={
            "amount": 55000.00,
            "category": "Salary"
        })
        self.assertEqual(upd_res.status_code, 200)

        # 4. Check dashboard summary
        dash_res = self.client.get("/api/dashboard/summary?period=month")
        dash_data = dash_res.get_json()["data"]
        self.assertEqual(dash_data["total_income"], 55000.00)
        self.assertEqual(dash_data["total_expenses"], 15000.00)
        self.assertEqual(dash_data["net_balance"], 40000.00)

        # 5. Delete Expense
        del_res = self.client.delete(f"/api/transactions/{exp_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.get_json()["account_balance"], 80000.00)

    def test_04_atomic_transfer(self):
        """Test money transfer between accounts, balance check, and total balance preservation"""
        user = self.login_test_user()
        bank_acc = Account.query.filter_by(user_id=user.id, account_type="Bank Account").first()
        cash_acc = Account.query.filter_by(user_id=user.id, account_type="Cash").first()

        initial_total = self.client.get("/api/accounts").get_json()["total_balance"]

        # Transfer ₹5,000 from Bank to Cash
        trans_res = self.client.post("/api/transfers", json={
            "amount": 5000.00,
            "from_account_id": bank_acc.id,
            "to_account_id": cash_acc.id,
            "date": "2026-10-05",
            "time": "12:00",
            "note": "ATM Cash withdrawal"
        })
        self.assertEqual(trans_res.status_code, 201)
        trans_data = trans_res.get_json()
        self.assertEqual(trans_data["from_account_balance"], 20000.00) # 25000 - 5000
        self.assertEqual(trans_data["to_account_balance"], 8000.00)   # 3000 + 5000
        # Critical Requirement: Total net balance must remain unchanged!
        self.assertEqual(trans_data["total_balance"], initial_total)

        # Insufficient funds check
        fail_res = self.client.post("/api/transfers", json={
            "amount": 999999.00,
            "from_account_id": bank_acc.id,
            "to_account_id": cash_acc.id,
            "date": "2026-10-05",
            "time": "12:00"
        })
        self.assertEqual(fail_res.status_code, 400)
        self.assertIn("Insufficient funds", fail_res.get_json()["error"])

    def test_05_notes_crud(self):
        """Test notes creation, editing, searching, and deletion"""
        user = self.login_test_user()

        # Create note
        res = self.client.post("/api/notes", json={
            "title": "Emergency Fund Goal",
            "content": "Keep at least 6 months living expenses in savings."
        })
        self.assertEqual(res.status_code, 201)
        note_id = res.get_json()["note"]["id"]

        # Search notes
        search_res = self.client.get("/api/notes?search=Emergency")
        self.assertEqual(len(search_res.get_json()["notes"]), 1)

        # Update note
        upd_res = self.client.put(f"/api/notes/{note_id}", json={
            "title": "Updated Emergency Goal",
            "content": "Revised to 9 months."
        })
        self.assertEqual(upd_res.status_code, 200)

        # Delete note
        del_res = self.client.delete(f"/api/notes/{note_id}")
        self.assertEqual(del_res.status_code, 200)

    def test_06_excel_export_multi_sheet(self):
        """Test 5-sheet Excel workbook export using Pandas and OpenPyXL"""
        user = self.login_test_user()
        bank_acc = Account.query.filter_by(user_id=user.id, account_type="Bank Account").first()

        # Add sample transaction
        self.client.post("/api/transactions", json={
            "transaction_type": "income",
            "amount": 25000.00,
            "category": "Salary",
            "account_id": bank_acc.id,
            "date": "2026-10-01",
            "time": "10:00",
            "description": "Consulting"
        })

        # Request Excel download
        res = self.client.get("/api/export/excel?type=all&month=10&year=2026")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Parse Excel workbook with OpenPyXL
        excel_bytes = io.BytesIO(res.data)
        wb = openpyxl.load_workbook(excel_bytes)
        expected_sheets = ["All Transactions", "Income Summary", "Expense Summary", "Transfers", "Account Summary"]
        for sheet in expected_sheets:
            self.assertIn(sheet, wb.sheetnames)

        # Check Sheet 1 has data
        ws1 = wb["All Transactions"]
        self.assertGreaterEqual(ws1.max_row, 3)

    def test_07_analytics_and_statistics(self):
        """Test 8-chart statistics API response format"""
        user = self.login_test_user()
        # Seed demo data
        self.client.post("/api/settings/seed-sample-data")

        # Request monthly statistics
        res = self.client.get("/api/statistics?filter=monthly&year=2026&month=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        # Validate all 8 charts datasets exist
        charts = data["charts"]
        self.assertIn("expense_categories", charts)
        self.assertIn("income_categories", charts)
        self.assertIn("daily_trends", charts)
        self.assertIn("income_vs_expense", charts)
        self.assertIn("monthly_expenses", charts)
        self.assertIn("yearly_trends", charts)
        self.assertIn("transfers_by_source", charts)
        self.assertIn("spending_comparison", charts)

        # Validate Monthly Overview API
        mo_res = self.client.get("/api/monthly-overview?year=2026&month=10")
        self.assertEqual(mo_res.status_code, 200)
        mo_data = mo_res.get_json()["data"]
        self.assertIn("comparison", mo_data)
        self.assertIn("expense_breakdown", mo_data)

if __name__ == "__main__":
    unittest.main()
