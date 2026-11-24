from datetime import datetime
from decimal import Decimal
from database.db import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), default="MoneyMate User")
    timezone = db.Column(db.String(50), default="Asia/Kolkata")
    currency = db.Column(db.String(10), default="₹")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    accounts = db.relationship("Account", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    transactions = db.relationship("Transaction", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    notes = db.relationship("Note", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "name": self.name,
            "timezone": self.timezone,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Account(db.Model):
    __tablename__ = "accounts"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False) # 'Cash', 'Bank Account', 'Card'
    opening_balance = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    archived_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, current_balance=None):
        bal = current_balance if current_balance is not None else float(self.opening_balance or 0.0)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "opening_balance": float(self.opening_balance or 0.0),
            "current_balance": round(bal, 2),
            "is_archived": self.is_archived,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

class Transaction(db.Model):
    __tablename__ = "transactions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False, index=True) # 'income', 'expense', 'transfer'
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    category = db.Column(db.String(50), nullable=True, index=True)
    
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    
    description = db.Column(db.String(255), nullable=True)
    note = db.Column(db.Text, nullable=True)
    transaction_datetime = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = db.relationship("Account", foreign_keys=[account_id], lazy="joined")
    from_account = db.relationship("Account", foreign_keys=[from_account_id], lazy="joined")
    to_account = db.relationship("Account", foreign_keys=[to_account_id], lazy="joined")
    
    def to_dict(self):
        dt = self.transaction_datetime
        return {
            "id": self.id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "amount": float(self.amount),
            "category": self.category or ("Transfer" if self.transaction_type == "transfer" else "Other"),
            "account_id": self.account_id,
            "account_name": self.account.account_name if self.account else None,
            "from_account_id": self.from_account_id,
            "from_account_name": self.from_account.account_name if self.from_account else None,
            "to_account_id": self.to_account_id,
            "to_account_name": self.to_account.account_name if self.to_account else None,
            "description": self.description or "",
            "note": self.note or "",
            "date": dt.strftime("%Y-%m-%d") if dt else "",
            "time": dt.strftime("%H:%M") if dt else "",
            "transaction_datetime": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }

class Note(db.Model):
    __tablename__ = "notes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transaction = db.relationship("Transaction", foreign_keys=[transaction_id], lazy="joined")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "transaction_id": self.transaction_id,
            "transaction_desc": (self.transaction.description or self.transaction.category) if self.transaction else None,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else ""
        }

class OTPVerification(db.Model):
    __tablename__ = "otp_verifications"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
