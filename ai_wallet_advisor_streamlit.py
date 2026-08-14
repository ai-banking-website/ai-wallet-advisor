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
.stApp {
    background:
      radial-gradient(circle at 5% 5%, rgba(99,91,255,.12), transparent 24%),
      radial-gradient(circle at 95% 10%, rgba(6,182,212,.10), transparent 22%),
      linear-gradient(180deg,#fafaff 0%,#f2f8ff 100%);
}
.hero {
    border-radius:24px; padding:28px 32px; margin-bottom:20px; color:white;
    background:linear-gradient(135deg,#635bff,#8b5cf6,#06b6d4);
    box-shadow:0 14px 35px rgba(99,91,255,.20);
}
.hero h1 {color:white !important;margin:0 0 6px 0;}
.hero p {color:rgba(255,255,255,.9);margin:0;}
.pill {display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(255,255,255,.18);font-size:.78rem;font-weight:700;margin-bottom:8px;}
.feature {
    border-radius:18px;padding:16px;background:rgba(255,255,255,.88);
    border:1px solid rgba(99,91,255,.12);box-shadow:0 7px 20px rgba(30,41,59,.06);
    min-height:145px;
}
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

# Mark whether the user has completed the initial financial setup.
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False

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

def svg_illustration(kind):
    icons = {
        "wallet": """<svg viewBox="0 0 180 110" width="150"><rect x="22" y="28" width="136" height="64" rx="14" fill="#fff"/><rect x="82" y="48" width="76" height="30" rx="10" fill="#ddd9ff"/><circle cx="108" cy="63" r="6" fill="#635bff"/><path d="M38 28V20c0-8 7-14 15-14h75c8 0 15 6 15 14v8" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/></svg>""",
        "chart": """<svg viewBox="0 0 180 110" width="150"><rect x="22" y="65" width="25" height="30" rx="6" fill="#635bff"/><rect x="58" y="48" width="25" height="47" rx="6" fill="#8b5cf6"/><rect x="94" y="27" width="25" height="68" rx="6" fill="#06b6d4"/><path d="M25 36l40-16 34 11 48-24" fill="none" stroke="#10b981" stroke-width="6" stroke-linecap="round"/></svg>""",
        "goal": """<svg viewBox="0 0 180 110" width="150"><circle cx="90" cy="55" r="42" fill="#f1efff" stroke="#635bff" stroke-width="7"/><circle cx="90" cy="55" r="25" fill="none" stroke="#8b5cf6" stroke-width="7"/><circle cx="90" cy="55" r="9" fill="#06b6d4"/><path d="M130 16l25-10-10 24" fill="none" stroke="#10b981" stroke-width="7" stroke-linecap="round"/></svg>"""
    }
    return icons.get(kind, icons["wallet"])

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
    ["📊 Dashboard", "💰 Money Manager", "🤖 Advisor & Conclusion"],
    index=0 if st.session_state.profile_complete else 1
)

st.sidebar.divider()
st.sidebar.caption("3 simple sections • Profile, Dashboard & Insights")

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
if page == "📊 Dashboard":
    if not st.session_state.profile_complete:
        st.markdown("""
        <div class="card" style="padding:2.5rem; text-align:center;">
            <h1>📊 Your Dashboard</h1>
            <p style="font-size:1.15rem;">Your dashboard will appear here after you complete your Financial Profile.</p>
            <p>👈 Use <b>Financial Profile</b> in the sidebar to enter your numbers.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero">
            <span class="pill">✨ YOUR MONEY AT A GLANCE</span>
            <h1>📊 Financial Dashboard</h1>
            <p>See your cash flow, savings, investments, and goals in one simple view.</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("✨ Your money toolkit")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown(f'<div class="feature">{svg_illustration("wallet")}<h3>💰 Cash Flow</h3><p>See what comes in, what goes out, and what remains.</p></div>', unsafe_allow_html=True)
        with f2:
            st.markdown(f'<div class="feature">{svg_illustration("chart")}<h3>📈 Growth</h3><p>Keep an eye on savings and investments.</p></div>', unsafe_allow_html=True)
        with f3:
            st.markdown(f'<div class="feature">{svg_illustration("goal")}<h3>🎯 Goals</h3><p>Turn your plans into measurable progress.</p></div>', unsafe_allow_html=True)

        # Core KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Monthly income", money(income))
        c2.metric("💸 Monthly expenses", money(expenses))
        c3.metric("💵 Available", money(balance))
        c4.metric("📈 Investments", money(investments))

        st.subheader("📌 Financial health")
        h1, h2, h3 = st.columns(3)
        h1.metric("🏦 Current savings", money(current_savings))
        h2.metric("🎯 Savings goal", money(savings_goal))
        h3.metric("📊 Savings rate", f"{savings_rate:.1f}%")

        # Cash-flow visual
        st.subheader("💸 Where your monthly income goes")
        if income > 0:
            flow = pd.DataFrame({
                "Amount (₹)": [max(expenses, 0), max(monthly_investment, 0), max(balance - monthly_investment, 0)]
            }, index=["Expenses", "Investments", "Remaining"])
            st.bar_chart(flow)
        else:
            st.info("Add your income on the Financial Profile page to see your cash-flow chart.")

        left, right = st.columns(2)
        with left:
            st.markdown(
                '<div class="card"><h3>🤖 Quick insight</h3><p>' +
                advisor_message(income, expenses) +
                '</p></div>', unsafe_allow_html=True
            )
        with right:
            goal_gap = savings_goal - max(balance - monthly_investment, 0)
            if savings_goal > 0 and goal_gap <= 0:
                goal_text = "🎉 Your current monthly cash flow can cover your savings goal."
            elif savings_goal > 0:
                goal_text = f"🎯 You are about {money(goal_gap)} short of your monthly savings goal after expenses and investments."
            else:
                goal_text = "🎯 Set a monthly savings goal on Financial Profile to track it here."
            st.markdown(
                f'<div class="card"><h3>Goal check</h3><p>{goal_text}</p></div>',
                unsafe_allow_html=True
            )

        # Transactions are supporting data, not the source of profile inputs.
        st.subheader("🧾 Recent transactions")
        if not tx.empty:
            st.dataframe(tx.sort_values("Date", ascending=False).head(8), use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet. Add them from the Transactions page.")

        st.caption("To change your income, expenses, savings or investments, use Financial Profile in the sidebar.")

# ---------- Financial Profile ----------
elif page == "💰 Money Manager":
    st.markdown("""
    <div class="hero">
        <span class="pill">🧰 YOUR MONEY TOOLKIT</span>
        <h1>💰 Money Manager</h1>
        <p>Update your financial profile and manage the details behind your dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Enter or update your finances")

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
        st.session_state.profile_complete = True
        st.success("✅ Saved! Your Dashboard is now updated with these numbers.")
        st.rerun()

    st.divider()
    st.subheader("🧰 Manage your money")

    money_tab1, money_tab2, money_tab3 = st.tabs(["🧾 Transactions", "💳 Budget", "🎯 Goals"])

    with money_tab1:
        st.caption("Add, review, and manage your wallet activity.")
        with st.form("add_transaction_compact", clear_on_submit=True):
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
                amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
                typ = st.radio("Type", ["Income", "Expense"], horizontal=True)

            if st.form_submit_button("➕ Add transaction", type="primary"):
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

    with money_tab2:
        st.caption("Set monthly spending limits and compare them with your activity.")
        expense_tx = tx[tx["Amount"] < 0].copy()
        expense_tx["Spent"] = expense_tx["Amount"].abs()
        spent = expense_tx.groupby("Category")["Spent"].sum()

        categories = ["Food", "Transport", "Housing", "Entertainment",
                      "Shopping", "Bills", "Health", "Education", "Other"]

        if "budgets" not in st.session_state:
            st.session_state.budgets = {c: 5000.0 for c in categories}

        with st.form("budget_form_compact"):
            budget_cols = st.columns(3)
            new_budgets = {}
            for i, cat in enumerate(categories):
                with budget_cols[i % 3]:
                    new_budgets[cat] = st.number_input(
                        f"{cat} budget (₹)",
                        min_value=0.0,
                        value=float(st.session_state.budgets.get(cat, 5000.0)),
                        step=500.0,
                        key=f"budget_compact_{cat}"
                    )
            if st.form_submit_button("💾 Save budgets", type="primary"):
                st.session_state.budgets = new_budgets
                st.success("Budgets saved.")
                st.rerun()

        budget_rows=[]
        for cat in categories:
            limit=float(st.session_state.budgets.get(cat,0))
            actual=float(spent.get(cat,0))
            budget_rows.append({"Category":cat,"Budget (₹)":limit,"Spent (₹)":actual,"Remaining (₹)":limit-actual})
        st.dataframe(pd.DataFrame(budget_rows), use_container_width=True, hide_index=True)

    with money_tab3:
        st.caption("Set and track your savings goals.")
        with st.form("goal_form_compact", clear_on_submit=True):
            goal_name = st.text_input("Goal name")
            target = st.number_input("Target amount (₹)", min_value=0.0, step=1000.0)
            saved = st.number_input("Already saved (₹)", min_value=0.0, step=500.0)
            if st.form_submit_button("➕ Add goal", type="primary"):
                row = pd.DataFrame([{"Goal": goal_name or "New Goal", "Target": target, "Saved": saved}])
                st.session_state.goals = pd.concat([st.session_state.goals, row], ignore_index=True)
                st.success("Goal added.")
                st.rerun()

        for _, g in st.session_state.goals.iterrows():
            target=float(g["Target"]); saved=float(g["Saved"])
            progress=min(saved/target,1) if target else 0
            st.write(f"**{g['Goal']}** — {money(saved)} / {money(target)}")
            st.progress(progress)

# ---------- Transactions ----------

elif page == "__legacy__":
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
elif page == "__legacy__":
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
elif page == "__legacy__":
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
elif page == "🤖 Advisor & Conclusion":
    st.title("🤖 AI Advisor")
    st.caption("Educational guidance based on the information in your wallet.")

    if not st.session_state.profile_complete:
        st.warning("Please complete the financial setup on the Dashboard first.")
    else:
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
elif page == "__legacy__":
    st.title("✨ Conclusion")
    st.caption("A simple summary of the financial information you entered.")

    if not st.session_state.profile_complete:
        st.warning("Complete the financial setup on the Dashboard first.")
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
