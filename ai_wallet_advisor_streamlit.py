import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import date

st.set_page_config(
    page_title="AI Wallet Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
[data-testid="stMetricValue"] {font-size: 1.7rem;}
.card {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 14px;
    background: rgba(255,255,255,.55);
    margin-bottom: .8rem;
}
.small {font-size:.9rem; opacity:.75;}
</style>
""", unsafe_allow_html=True)

# ---------- Financial profile state ----------
if "financial_profile" not in st.session_state:
    st.session_state.financial_profile = {
        "income": 0.0,
        "expenditure": 0.0,
        "savings": 0.0,
        "investments": 0.0,
        "monthly_investment": 0.0,
        "savings_goal": 0.0,
    }

# ---------- Session state ----------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame([
        {"Date": date.today(), "Description": "Salary", "Category": "Income", "Amount": 50000.0},
        {"Date": date.today(), "Description": "Groceries", "Category": "Food", "Amount": -3500.0},
        {"Date": date.today(), "Description": "Transport", "Category": "Transport", "Amount": -1800.0},
        {"Date": date.today(), "Description": "Entertainment", "Category": "Entertainment", "Amount": -1200.0},
    ])

if "goals" not in st.session_state:
    st.session_state.goals = pd.DataFrame([
        {"Goal": "Emergency Fund", "Target": 100000.0, "Saved": 35000.0},
        {"Goal": "New Laptop", "Target": 80000.0, "Saved": 20000.0},
    ])

# ---------- Helpers ----------
def money(x):
    return f"₹{x:,.0f}"

def advisor_message(income, expenses):
    if income <= 0:
        return "Add some income data to get a personalized budget insight."
    ratio = expenses / income
    if ratio > .8:
        return "Your spending is relatively high compared with your income. Review your largest expense categories first."
    if ratio > .6:
        return "You're in a reasonable range, but there is room to increase your savings rate."
    return "Great job! Your current spending leaves a healthy amount available for saving and goals."

# ---------- Sidebar ----------
st.sidebar.title("💰 AI Wallet Advisor")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Financial Profile", "Transactions", "Budget", "Goals", "Advisor", "Conclusion"]
)

st.sidebar.divider()
st.sidebar.caption("Streamlit version of your AI Wallet Advisor")

# ---------- Calculations ----------
tx = st.session_state.transactions.copy()
profile = st.session_state.financial_profile

# Use the user's explicit financial inputs when provided.
transaction_income = tx.loc[tx["Amount"] > 0, "Amount"].sum()
transaction_expenses = -tx.loc[tx["Amount"] < 0, "Amount"].sum()

income = float(profile["income"]) if profile["income"] > 0 else transaction_income
expenses = float(profile["expenditure"]) if profile["expenditure"] > 0 else transaction_expenses
current_savings = float(profile["savings"])
investments = float(profile["investments"])
monthly_investment = float(profile["monthly_investment"])
savings_goal = float(profile["savings_goal"])

balance = income - expenses
savings_rate = (balance / income * 100) if income else 0

# ---------- Dashboard ----------
if page == "Dashboard":
    st.title("AI Wallet Advisor")
    st.caption("Your personal finance dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Balance", money(balance))
    c2.metric("Income", money(income))
    c3.metric("Expenses", money(expenses))
    c4.metric("Savings", money(current_savings))

    c5, c6 = st.columns(2)
    c5.metric("Investments", money(investments))
    c6.metric("Savings Rate", f"{savings_rate:.1f}%")

    st.subheader("Spending overview")
    left, right = st.columns(2)

    with left:
        expense_data = tx[tx["Amount"] < 0].copy()
        if not expense_data.empty:
            expense_data["Amount"] = expense_data["Amount"].abs()
            by_cat = expense_data.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            st.bar_chart(by_cat)
        else:
            st.info("No expense data yet.")

    with right:
        st.markdown('<div class="card"><b>🤖 AI Insight</b><br><br>' +
                    advisor_message(income, expenses) +
                    '</div>', unsafe_allow_html=True)
        st.subheader("Goals progress")
        for _, g in st.session_state.goals.iterrows():
            progress = min(g["Saved"] / g["Target"], 1) if g["Target"] else 0
            st.write(f"**{g['Goal']}** — {money(g['Saved'])} / {money(g['Target'])}")
            st.progress(progress)

    st.subheader("Recent transactions")
    st.dataframe(tx.sort_values("Date", ascending=False).head(8),
                 use_container_width=True, hide_index=True)

# ---------- Financial Profile ----------
if page == "Financial Profile":
    st.markdown("""
    <div class="card">
        <h1>💵 Financial Profile</h1>
        <p>Enter your financial information so the dashboard, advisor, and conclusion can personalize their results.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Tell us about your finances")

    with st.form("financial_profile_form"):
        c1, c2 = st.columns(2)

        with c1:
            entered_income = st.number_input(
                "💰 Monthly income (₹)",
                min_value=0.0,
                value=float(profile["income"]),
                step=1000.0,
                help="Your usual monthly take-home income."
            )
            entered_expenditure = st.number_input(
                "💸 Monthly expenditure (₹)",
                min_value=0.0,
                value=float(profile["expenditure"]),
                step=500.0,
                help="Your usual monthly spending."
            )
            entered_savings = st.number_input(
                "🏦 Current savings (₹)",
                min_value=0.0,
                value=float(profile["savings"]),
                step=1000.0,
                help="Money you currently have saved."
            )

        with c2:
            entered_investments = st.number_input(
                "📈 Current investments (₹)",
                min_value=0.0,
                value=float(profile["investments"]),
                step=1000.0,
                help="Approximate current value of your investments."
            )
            entered_monthly_investment = st.number_input(
                "📊 Monthly investment contribution (₹)",
                min_value=0.0,
                value=float(profile["monthly_investment"]),
                step=500.0,
                help="How much you currently invest each month."
            )
            entered_savings_goal = st.number_input(
                "🎯 Monthly savings goal (₹)",
                min_value=0.0,
                value=float(profile["savings_goal"]),
                step=500.0,
                help="How much you want to save each month."
            )

        submitted = st.form_submit_button(
            "💾 Save financial information",
            type="primary",
            use_container_width=True
        )

    if submitted:
        st.session_state.financial_profile = {
            "income": entered_income,
            "expenditure": entered_expenditure,
            "savings": entered_savings,
            "investments": entered_investments,
            "monthly_investment": entered_monthly_investment,
            "savings_goal": entered_savings_goal,
        }
        st.success("✅ Financial information saved! Go to Dashboard, Advisor, or Conclusion to see the results.")
        st.rerun()

# ---------- Transactions ----------

elif page == "Transactions":
    st.title("Transactions")
    st.caption("Add, review, and manage your wallet activity.")

    with st.form("add_transaction", clear_on_submit=True):
        a, b, c = st.columns(3)
        with a:
            d = st.date_input("Date", date.today())
            desc = st.text_input("Description")
        with b:
            category = st.selectbox(
                "Category",
                ["Income", "Food", "Transport", "Housing", "Entertainment",
                 "Shopping", "Bills", "Health", "Education", "Other"]
            )
        with c:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                help="Use Type below to decide whether this is income or expense."
            )
            typ = st.radio("Type", ["Income", "Expense"], horizontal=True)

        submitted = st.form_submit_button("Add transaction", type="primary")
        if submitted:
            signed = amount if typ == "Income" else -amount
            new_row = pd.DataFrame([{
                "Date": d, "Description": desc or category,
                "Category": category if typ == "Expense" else "Income",
                "Amount": signed
            }])
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, new_row], ignore_index=True
            )
            st.success("Transaction added.")
            st.rerun()

    st.dataframe(
        st.session_state.transactions.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ---------- Budget ----------
elif page == "Budget":
    st.title("Budget")
    st.caption("Set monthly spending limits and compare them with your activity.")

    expense_tx = tx[tx["Amount"] < 0].copy()
    expense_tx["Spent"] = expense_tx["Amount"].abs()
    spent = expense_tx.groupby("Category")["Spent"].sum()

    categories = ["Food", "Transport", "Housing", "Entertainment",
                  "Shopping", "Bills", "Health", "Education", "Other"]

    if "budgets" not in st.session_state:
        st.session_state.budgets = {c: 5000.0 for c in categories}

    for cat in categories:
        current = float(spent.get(cat, 0))
        limit = st.number_input(
            cat, min_value=0.0, value=float(st.session_state.budgets[cat]),
            step=500.0, key=f"budget_{cat}"
        )
        st.session_state.budgets[cat] = limit
        pct = min(current / limit, 1) if limit else 0
        st.progress(pct)
        st.caption(f"Spent {money(current)} of {money(limit)}")

# ---------- Goals ----------
elif page == "Goals":
    st.title("Savings Goals")

    with st.form("goal_form", clear_on_submit=True):
        a, b, c = st.columns(3)
        with a:
            name = st.text_input("Goal name")
        with b:
            target = st.number_input("Target amount", min_value=0.0, step=1000.0)
        with c:
            saved = st.number_input("Already saved", min_value=0.0, step=1000.0)
        if st.form_submit_button("Add goal", type="primary"):
            st.session_state.goals = pd.concat([
                st.session_state.goals,
                pd.DataFrame([{"Goal": name or "New Goal",
                               "Target": target, "Saved": saved}])
            ], ignore_index=True)
            st.success("Goal added.")
            st.rerun()

    for i, g in st.session_state.goals.iterrows():
        progress = min(g["Saved"] / g["Target"], 1) if g["Target"] else 0
        st.markdown(f"### {g['Goal']}")
        st.progress(progress)
        st.write(f"{money(g['Saved'])} saved of {money(g['Target'])} — **{progress*100:.0f}%**")
        if progress >= 1:
            st.success("Goal reached! 🎉")

# ---------- Advisor ----------
elif page == "Advisor":
    st.title("🤖 AI Advisor")
    st.caption("Educational guidance based on the information in your wallet.")

    st.info(advisor_message(income, expenses))

    st.subheader("Ask for an analysis")
    question = st.text_area(
        "What would you like help with?",
        placeholder="Example: How can I save more money each month?"
    )

    if st.button("Analyze", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            st.write("### Suggested approach")
            st.write(
                f"Based on your current numbers — income of {money(income)}, "
                f"expenses of {money(expenses)}, and a balance of {money(balance)} — "
                "start by reviewing your largest spending category, then set a "
                "specific savings target. This is educational guidance, not financial advice."
            )

    st.subheader("Wallet summary")
    st.json({
        "income": round(float(income), 2),
        "expenses": round(float(expenses), 2),
        "balance": round(float(balance), 2),
        "savings_rate_percent": round(float(savings_rate), 2),
    })

# ---------- Conclusion ----------
elif page == "Conclusion":
    st.title("✨ Conclusion")
    st.caption("A simple summary of the financial information you entered.")

    if income <= 0 and expenses <= 0 and current_savings <= 0 and investments <= 0:
        st.warning("Enter your information on the Financial Profile page first.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Monthly income", money(income))
        c2.metric("Monthly expenditure", money(expenses))
        c3.metric("Current savings", money(current_savings))
        c4.metric("Investments", money(investments))

        st.subheader("🔎 Overall assessment")

        if income > 0 and expenses > income:
            st.error(
                f"Your expenditure is {money(expenses - income)} higher than your monthly income. "
                "Improving your monthly cash flow should be a priority."
            )
        elif income > 0 and expenses >= income * 0.7:
            st.warning(
                "Your expenditure uses a large share of your income. "
                "Review your biggest recurring expenses."
            )
        elif income > 0:
            st.success(
                "Your expenditure is below 70% of your income, leaving room for saving and investing."
            )

        remaining_after_investment = income - expenses - monthly_investment

        st.subheader("🎯 Your next steps")
        steps = [
            "Keep regular spending below your income.",
            f"Work toward your monthly savings goal of {money(savings_goal)}." if savings_goal > 0 else "Set a specific monthly savings goal.",
            f"Review your current investment contribution of {money(monthly_investment)} against your goals and risk tolerance." if monthly_investment > 0 else "If you plan to invest, research options carefully and consider your goals and risk tolerance.",
            "Update your Financial Profile whenever your income, spending, savings, or investments change.",
        ]
        for i, step in enumerate(steps, 1):
            st.markdown(f'<div class="card"><b>{i}.</b> {step}</div>', unsafe_allow_html=True)

        st.subheader("💡 Final takeaway")
        st.info(
            f"Based on the numbers you entered, you have approximately {money(balance)} "
            f"left after monthly expenditure. After your current monthly investment contribution, "
            f"that becomes approximately {money(remaining_after_investment)}."
        )

        st.caption(
            "This app provides general educational information and is not personalized financial advice."
        )

st.divider()
st.caption("AI Wallet Advisor • For educational purposes only")
