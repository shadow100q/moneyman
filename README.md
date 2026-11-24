# MoneyMate — Personal Money Management System

A modern, full-stack, responsive personal finance web application built with **Python Flask**, **MySQL**, **HTML5/CSS3/JavaScript**, **Chart.js**, and **Pandas / OpenPyXL**.

---

## 🌟 Key Features

1. **Secure Phone-Number Authentication with OTP Verification:**
   - 6-digit cryptographic OTP generation with SHA-256 hashing.
   - 5-minute expiration, 60-second resend cooldown, and rate limiting (max 5 attempts).
   - **Zero-Friction Dev OTP Mode:** Prominently displays the generated OTP with an "Auto-fill OTP" button for local testing without requiring an external SMS provider.
   - Pluggable SMS gateway support (Twilio / configurable provider).

2. **Home Dashboard:**
   - Real-time period switcher: **Today**, **This Week**, **This Month**, and **Custom Date Range**.
   - **5 Summary Cards:** Total Balance across accounts, Total Income, Total Expenses, Net Savings (Income - Expenses), and Total Transfers (strictly separated from earnings/spendings).
   - Prominent **Today's Activity** focus banner.
   - **Quick Actions:** Modal dialogs for instant Income, Expense, Transfer, and Note creation with dynamic dashboard updates without requiring full-page reload.
   - Recent activity list with interactive filtering tabs (All, Income, Expense, Transfer).
   - Live My Accounts widget and Quick Notes widget.

3. **Income & Expense Tracking:**
   - Standardized categories:
     - **Income:** Allowance, Salary, Petty Cash, Bonus, Other.
     - **Expense:** Food, Social Life, Pets, Transport, Culture, Household, Apparel, Beauty, Health, Education, Gift, Other.
   - Auto-populated local date & time (Asia/Kolkata default, editable).
   - Full CRUD: Add, edit, and delete transactions with confirmation and automatic balance recalculations.

4. **Atomic Money Transfers:**
   - Move funds between user accounts (e.g., Bank Account → Cash Wallet or Credit Card).
   - Source available balance validation and overdraft protection.
   - Atomic database transactions ensure balance integrity.
   - Transfers never inflate income or expense metrics; total net wealth remains constant.
   - Supports editing and deleting transfers with balance reversal.

5. **All Transactions & Historical Month Navigation:**
   - **Essential Month Navigator:** Move seamlessly between past and future months (`← Previous Month`, `Next Month →`, direct Month & Year dropdown pickers, and `Current Month` button).
   - Monthly summary counters: Total Income, Total Expenses, Net Savings, Total Transfers, and Transaction count.
   - Multi-field search, filtering by Type, Category, and Account.
   - Newest / Oldest sorting and pagination.

6. **Monthly Financial Overview:**
   - Deep dive into any selected month with direct comparison to the previous month (delta amounts and percentage changes).
   - Daily income vs expense trend line chart.
   - Expense and income category breakdown progress bars.
   - Top 5 highest spending categories.
   - Account balances overview.

7. **Statistics & Analytics (8 Chart.js Visualizations):**
   - Time filters: **Weekly**, **Monthly**, **Yearly**, and **Custom Date Range**.
   - 8 Charts:
     1. *Expense Categories Breakdown* (Doughnut chart)
     2. *Income Sources Breakdown* (Pie chart)
     3. *Daily Financial Trends* (Line chart)
     4. *Income vs Expenses Comparison* (Bar chart)
     5. *Monthly Expenses over 12 Months* (Bar chart)
     6. *Yearly Financial Trends* (Line chart)
     7. *Transfers by Source Account* (Bar chart)
     8. *Category-Wise Spending Ranking* (Horizontal bar chart)

8. **Account Management:**
   - Accounts supporting Cash, Bank Account, and Card types.
   - Opening balances and real-time calculated balances.
   - Safe archiving and deletion protection (prevents deleting accounts with transaction history).
   - Drilldown modal to inspect all transactions linked to a specific account.

9. **Personal Notes:**
   - Financial notes and reminders.
   - Full CRUD with search and optional transaction linkage.

10. **Excel Workbook Export (.xlsx):**
    - Dynamic multi-sheet Excel generation using **Pandas** and **OpenPyXL**.
    - Configurable filters: Month/Year, Custom Date Range, Transaction Type, Account, and Category.
    - **5 Formatted Sheets:**
      - *Sheet 1:* All Transactions
      - *Sheet 2:* Income Summary (by category and by month)
      - *Sheet 3:* Expense Summary (by category and by month)
      - *Sheet 4:* Transfers (audit trail of money movements)
      - *Sheet 5:* Account Summary (opening vs current balances)
    - Professional header styling, auto column widths, currency formatting, and frozen top rows.

---

## 🏗️ Project Architecture

```text
money management system/
├── app.py                      # Flask Application entry point & configuration
├── config.py                   # App settings, DB URI, OTP configs, and session rules
├── models.py                   # SQLAlchemy Models (User, Account, Transaction, Note, OTP)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Complete documentation
├── database/
│   ├── db.py                   # Database initialization with resilient SQLite fallback
│   ├── schema.sql              # Clean MySQL database schema script
│   └── seed.sql                # MySQL seed script for testing
├── routes/
│   ├── auth_routes.py          # OTP login, verification, and session control
│   ├── account_routes.py       # Account CRUD, balances, and archiving
│   ├── transaction_routes.py   # Income, expense, and ledger history
│   ├── transfer_routes.py      # Atomic transfers and validations
│   ├── dashboard_routes.py     # Dashboard summaries and recent activity feeds
│   ├── statistics_routes.py    # Analytics endpoints and monthly comparison
│   ├── notes_routes.py         # Notes CRUD and search
│   ├── export_routes.py        # Excel workbook export (.xlsx)
│   └── settings_routes.py      # Profile preferences and one-click demo data
├── services/
│   ├── balance_service.py      # Accurate multi-account balance math
│   ├── statistics_service.py   # Metric aggregation & Chart.js data formatting
│   └── export_service.py       # Multi-sheet Excel workbook builder
├── templates/
│   ├── base.html               # Sidebar layout, mobile navigation, quick modals
│   ├── login.html              # OTP login page with dev mode banner
│   ├── dashboard.html          # Home dashboard
│   ├── income.html             # Add Income & history table
│   ├── expenses.html           # Add Expense & history table
│   ├── transfers.html          # Transfers form & history table
│   ├── transactions.html       # All transactions with month-by-month navigation
│   ├── monthly_overview.html   # Monthly deep dive & previous month comparison
│   ├── statistics.html         # 8 Chart.js interactive charts
│   ├── notes.html              # Notes cards & search
│   ├── accounts.html           # Account management & transaction drilldowns
│   ├── export.html             # Excel export hub
│   └── settings.html           # User profile, system info & demo data seeder
└── static/
    ├── css/
    │   └── style.css           # Modern design system, responsive grid & dark/light accents
    └── js/
        ├── app.js              # Global utilities, toasts, modals, currency formatting
        ├── dashboard.js        # Dashboard real-time data & quick actions
        ├── transactions.js     # Ledger search, filters, pagination, and month navigation
        └── statistics.js       # 8 Chart.js rendering & filtering logic
```

---

## 🚀 Quick Setup & Installation

### 1. Prerequisites
- Python 3.10+
- MySQL Server (optional; if MySQL is not running locally, MoneyMate automatically falls back to an embedded SQLite database `moneymate.db` for instant zero-downtime execution!)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database (.env)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

#### If using MySQL:
1. Start your local MySQL server (or XAMPP/WAMP/Docker).
2. Create the database:
   ```sql
   CREATE DATABASE moneymate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. (Optional) Run the schema script:
   ```bash
   mysql -u root -p moneymate < database/schema.sql
   ```
4. Set credentials in `.env`:
   ```env
   USE_SQLITE=false
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DB=moneymate
   ```

#### If using SQLite (No MySQL server required):
In `.env`, simply ensure:
```env
USE_SQLITE=true
```

### 4. Start the Application
```bash
python app.py
```
The server will start at:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Authentication Guide

1. Open `http://127.0.0.1:5000` in your browser. You will be greeted by the login screen.
2. Enter any 10-digit phone number (e.g., `9876543210`) and click **Send Verification Code**.
3. In Development Mode (`DEV_OTP_MODE=true`), the 6-digit OTP code will appear right on screen in the **⚡ DEV MODE TEST OTP** box.
4. Click **Auto-Fill OTP & Verify** (or type the code) and you will be immediately logged into your dashboard!
5. On your first login, 3 default accounts are automatically provisioned:
   - *Main Bank Account* (Bank Account — ₹25,000.00)
   - *Cash Wallet* (Cash — ₹3,000.00)
   - *Credit Card* (Card — ₹0.00)

---

## 📊 Exploring Sample Historical Data

To immediately test all 8 charts, month-by-month historical navigation, category rankings, and Excel exports without manually entering dozens of records:
1. Navigate to **Settings** in the sidebar.
2. Under **Instant Testing & Demo Data**, click **Populate Rich Demo Data**.
3. MoneyMate will instantly seed past and current months with realistic Salaries, Grocery bills, Rent, Social dinners, Insurance payments, ATM transfers, and Notes!

---

## 📥 Excel Export (.xlsx)

1. Navigate to **Export Data** in the sidebar.
2. Choose your desired scope (Selected Month, Custom Date Range, or All Time), and optional filters (Transaction Type, Account, Category).
3. Click **Download Excel Workbook (.xlsx)**.
4. Open the generated spreadsheet in Microsoft Excel, Google Sheets, or LibreOffice to inspect all 5 styled sheets!
