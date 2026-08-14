import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta

# ============================================================
# AI WALLET ADVISOR — ULTIMATE EDITION
# A polished, interactive, educational personal-finance dashboard.
# ============================================================

st.set_page_config(
    page_title="AI Wallet Advisor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    max-width: 1500px;
}

.hero {
    padding: 2rem;
    border-radius: 24px;
    margin-bottom: 1.2rem;
    background: linear-gradient(135deg, #111827 0%, #312e81 48%, #0f766e 100%);
    color: white;
    box-shadow: 0 18px 45px rgba(15,23,42,.18);
}
.hero h1 { margin: 0; font-size: 2.35rem; font-weight: 800; }
.hero p { margin: .45rem 0 0; opacity: .86; }

.card {
    padding: 1.15rem 1.25rem;
    border: 1px solid rgba(100,116,139,.18);
    border-radius: 18px;
    background: rgba(255,255,255,.72);
    box-shadow: 0 8px 24px rgba(15,23,42,.05);
    margin-bottom: .9rem;
}
.dark-card {
    padding: 1.25rem;
    border-radius: 18px;
    background: #111827;
    color: white;
    margin-bottom: .9rem;
}
.kpi {
    padding: 1rem 1.1rem;
    border-radius: 17px;
    border: 1px solid rgba(100,116,139,.16);
    background: rgba(255,255,255,.78);
}
.kpi-label { font-size: .82rem; opacity: .65; font-weight: 600; }
.kpi-value { font-size: 1.65rem; font-weight: 800; margin-top: .15rem; }
.kpi-note { font-size: .78rem; opacity: .65; margin-top: .2rem; }
.small { font-size: .84rem; opacity: .7; }
.badge {
    display: inline-block;
    padding: .28rem .65rem;
    border-radius: 999px;
    font-size: .76rem;
    font-weight: 700;
    background: rgba(79,70,229,.10);
}
.section-title { font-size: 1.25rem; font-weight: 800; margin: .4rem 0 .8rem; }
.goal-title { font-weight: 800; font-size: 1.02rem; }
.insight {
    padding: 1rem 1.1rem;
    border-radius: 15px;
    background: rgba(79,70,229,.07);
    border-left: 4px solid #4f46e5;
    margin-bottom: .7rem;
}
div[data-testid="stMetricValue"] { font-size: 1.45rem; font-weight: 800; }
button[kind="primary"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- State -----------------------------
def default_profile():
    return {
        "income": 0.0,
        "expenditure": 0.0,
        "savings": 0.0,
        "investments": 0.0,
        "monthly_investment": 0.0,
        "savings_goal": 0.0,
    }

if "financial_profile" not in st.session_state:
    st.session_state.financial_profile = default_profile()

if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False

if "transactions" not in st.session_state:
    today = date.today()
    st.session_state.transactions = pd.DataFrame([
        {"Date": today, "Description": "Salary", "Category": "Income", "Amount": 50000.0},
        {"Date": today, "Description": "Groceries", "Category": "Food", "Amount": -3500.0},
        {"Date": today - timedelta(days=2), "Description": "Transport", "Category": "Transport", "Amount": -1800.0},
        {"Date": today - timedelta(days=4), "Description": "Entertainment", "Category": "Entertainment", "Amount": -1200.0},
    ])

if "goals" not in st.session_state:
    st.session_state.goals = pd.DataFrame([
        {"Goal": "Emergency Fund", "Target": 100000.0, "Saved": 35000.0, "Deadline": date.today() + timedelta(days=180)},
        {"Goal": "New Laptop", "Target": 80000.0, "Saved": 20000.0, "Deadline": date.today() + timedelta(days=240)},
    ])

if "budgets" not in st.session_state:
    st.session_state.budgets = {
        c: 5000.0 for c in [
            "Food", "Transport", "Housing", "Entertainment",
            "Shopping", "Bills", "Health", "Education", "Other"
        ]
    }

# ----------------------------- Helpers -----------------------------
def money(x):
    return f"₹{float(x):,.0f}"

def pct(x):
    return f"{float(x):.1f}%"

def calculate_metrics():
    tx = st.session_state.transactions.copy()
    profile = st.session_state.financial_profile

    tx_income = tx.loc[tx["Amount"] > 0, "Amount"].sum()
    tx_expenses = -tx.loc[tx["Amount"] < 0, "Amount"].sum()

    income = float(profile["income"]) if profile["income"] > 0 else float(tx_income)
    expenses = float(profile["expenditure"]) if profile["expenditure"] > 0 else float(tx_expenses)
    savings = float(profile["savings"])
    investments = float(profile["investments"])
    monthly_investment = float(profile["monthly_investment"])
    savings_goal = float(profile["savings_goal"])

    balance = income - expenses
    savings_rate = balance / income * 100 if income else 0
    expense_ratio = expenses / income * 100 if income else 0
    net_worth = savings + investments
    invest_rate = monthly_investment / income * 100 if income else 0
    emergency_months = savings / expenses if expenses > 0 else 0

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "investments": investments,
        "monthly_investment": monthly_investment,
        "savings_goal": savings_goal,
        "balance": balance,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "net_worth": net_worth,
        "invest_rate": invest_rate,
        "emergency_months": emergency_months,
    }

def health_score(m):
    score = 50
    if m["income"] > 0:
        score += 15 if m["balance"] > 0 else -20
        score += 10 if m["savings_rate"] >= 20 else 4 if m["savings_rate"] >= 10 else -5
        score += 10 if m["expense_ratio"] <= 60 else 4 if m["expense_ratio"] <= 80 else -10
        score += 10 if m["emergency_months"] >= 3 else 4 if m["emergency_months"] >= 1 else -4
        score += 5 if m["invest_rate"] >= 10 else 2 if m["invest_rate"] > 0 else 0
    return int(max(0, min(100, score)))

def health_label(score):
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Healthy"
    if score >= 50:
        return "Getting there"
    return "Needs attention"

def advisor_message(m):
    if m["income"] <= 0:
        return "Add your income to unlock personalized insights."
    if m["balance"] < 0:
        return "Your monthly spending is above income. Start by identifying the largest flexible expense."
    if m["expense_ratio"] > 80:
        return "Your spending takes a large share of income. A few targeted cuts could create breathing room."
    if m["savings_rate"] < 10:
        return "Your cash flow is positive, but your savings rate is low. Try setting a small automatic monthly target."
    if m["savings_rate"] >= 20 and m["emergency_months"] >= 3:
        return "Strong position: you have positive cash flow and a solid savings buffer. Keep your system consistent."
    return "You're on the right track. Focus on consistency: control spending, build savings, and invest according to your goals and risk tolerance."

def top_expenses():
    tx = st.session_state.transactions
    e = tx[tx["Amount"] < 0].copy()
    if e.empty:
        return pd.Series(dtype=float)
    e["Spent"] = e["Amount"].abs()
    return e.groupby("Category")["Spent"].sum().sort_values(ascending=False)

def render_kpi(label, value, note=""):
    st.markdown(
        f"""<div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
        </div>""",
        unsafe_allow_html=True
    )

# ----------------------------- Sidebar -----------------------------
st.sidebar.markdown("## 💎 AI Wallet Advisor")
st.sidebar.caption("Your smarter money dashboard")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "👤 Financial Profile", "💳 Transactions",
     "📊 Budget", "🎯 Goals", "🤖 Advisor", "✨ Conclusion"],
)

st.sidebar.divider()
m = calculate_metrics()
score = health_score(m)

st.sidebar.markdown("### Wallet health")
st.sidebar.progress(score / 100)
st.sidebar.markdown(f"**{score}/100 — {health_label(score)}**")
st.sidebar.caption("Educational score based on cash flow, spending, savings and investing.")

if st.sidebar.button("🔄 Reset demo data", use_container_width=True):
    for key in ["financial_profile", "transactions", "goals", "budgets"]:
        st.session_state.pop(key, None)
    st.session_state.profile_complete = False
    st.rerun()

# ----------------------------- Welcome / Setup -----------------------------
if page == "🏠 Dashboard" and not st.session_state.profile_complete:
    st.markdown("""
    <div class="hero">
        <h1>💎 Welcome to AI Wallet Advisor</h1>
        <p>A cleaner, smarter and more interactive way to understand your money.</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Start by entering your financial numbers. You can edit everything later.")

    with st.form("initial_setup"):
        st.markdown("### 🚀 Build your wallet profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            setup_income = st.number_input("Monthly income (₹)", min_value=0.0, step=1000.0)
            setup_expenditure = st.number_input("Monthly expenditure (₹)", min_value=0.0, step=500.0)
        with c2:
            setup_savings = st.number_input("Current savings (₹)", min_value=0.0, step=1000.0)
            setup_investments = st.number_input("Current investments (₹)", min_value=0.0, step=1000.0)
        with c3:
            setup_monthly_investment = st.number_input("Monthly investment (₹)", min_value=0.0, step=500.0)
            setup_savings_goal = st.number_input("Monthly savings goal (₹)", min_value=0.0, step=500.0)

        submitted = st.form_submit_button("🚀 Launch my dashboard", type="primary", use_container_width=True)

    if submitted:
        st.session_state.financial_profile = {
            "income": setup_income,
            "expenditure": setup_expenditure,
            "savings": setup_savings,
            "investments": setup_investments,
            "monthly_investment": setup_monthly_investment,
            "savings_goal": setup_savings_goal,
        }
        st.session_state.profile_complete = True
        st.success("Your wallet is ready!")
        st.rerun()

# ----------------------------- Dashboard -----------------------------
elif page == "🏠 Dashboard":
    m = calculate_metrics()
    score = health_score(m)
    top = top_expenses()

    st.markdown("""
    <div class="hero">
        <h1>💎 Your Money Command Center</h1>
        <p>See the big picture, spot problems early and turn your goals into a plan.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Monthly balance", money(m["balance"]), "Income − expenditure")
    with c2: render_kpi("Income", money(m["income"]), "Monthly")
    with c3: render_kpi("Expenses", money(m["expenses"]), f"{pct(m['expense_ratio'])} of income")
    with c4: render_kpi("Net worth", money(m["net_worth"]), "Savings + investments")

    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_kpi("Savings rate", pct(m["savings_rate"]), "Target: build consistency")
    with c2: render_kpi("Investing rate", pct(m["invest_rate"]), "Monthly contribution")
    with c3: render_kpi("Emergency runway", f"{m['emergency_months']:.1f} mo", "Savings ÷ monthly expenses")
    with c4: render_kpi("Health score", f"{score}/100", health_label(score))

    st.write("")
    left, right = st.columns([1.45, 1])

    with left:
        st.markdown('<div class="section-title">📈 Spending breakdown</div>', unsafe_allow_html=True)
        if not top.empty:
            st.bar_chart(top)
        else:
            st.info("Add expenses to see your spending breakdown.")

    with right:
        st.markdown('<div class="section-title">🤖 Smart insight</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight">{advisor_message(m)}</div>', unsafe_allow_html=True)
        if m["savings_goal"] > 0:
            gap = m["savings_goal"] - m["balance"]
            if gap > 0:
                st.warning(f"You are about {money(gap)} below your monthly savings target.")
            else:
                st.success(f"You're above your monthly savings target by {money(abs(gap))}.")

    st.markdown('<div class="section-title">🎯 Goal snapshot</div>', unsafe_allow_html=True)
    cols = st.columns(min(3, max(1, len(st.session_state.goals))))
    for idx, (_, g) in enumerate(st.session_state.goals.iterrows()):
        progress = min(float(g["Saved"]) / float(g["Target"]), 1) if g["Target"] else 0
        with cols[idx % len(cols)]:
            st.markdown(f'<div class="card"><div class="goal-title">{g["Goal"]}</div>'
                        f'<div class="small">{money(g["Saved"])} of {money(g["Target"])}</div></div>',
                        unsafe_allow_html=True)
            st.progress(progress)

    st.markdown('<div class="section-title">🧾 Recent activity</div>', unsafe_allow_html=True)
    recent = st.session_state.transactions.sort_values("Date", ascending=False).head(8).copy()
    if not recent.empty:
        recent["Amount"] = recent["Amount"].map(money)
        st.dataframe(recent, use_container_width=True, hide_index=True)

# ----------------------------- Profile -----------------------------
elif page == "👤 Financial Profile":
    st.markdown("""
    <div class="hero">
        <h1>👤 Financial Profile</h1>
        <p>One place to keep the numbers behind every dashboard calculation.</p>
    </div>
    """, unsafe_allow_html=True)

    p = st.session_state.financial_profile
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            income = st.number_input("💰 Monthly income (₹)", min_value=0.0, value=float(p["income"]), step=1000.0)
            expenditure = st.number_input("💸 Monthly expenditure (₹)", min_value=0.0, value=float(p["expenditure"]), step=500.0)
            savings = st.number_input("🏦 Current savings (₹)", min_value=0.0, value=float(p["savings"]), step=1000.0)
        with c2:
            investments = st.number_input("📈 Current investments (₹)", min_value=0.0, value=float(p["investments"]), step=1000.0)
            monthly_investment = st.number_input("📊 Monthly investment (₹)", min_value=0.0, value=float(p["monthly_investment"]), step=500.0)
            savings_goal = st.number_input("🎯 Monthly savings goal (₹)", min_value=0.0, value=float(p["savings_goal"]), step=500.0)

        if st.form_submit_button("💾 Save profile", type="primary", use_container_width=True):
            st.session_state.financial_profile = {
                "income": income, "expenditure": expenditure, "savings": savings,
                "investments": investments, "monthly_investment": monthly_investment,
                "savings_goal": savings_goal
            }
            st.session_state.profile_complete = True
            st.success("Profile updated!")
            st.rerun()

# ----------------------------- Transactions -----------------------------
elif page == "💳 Transactions":
    st.markdown("""
    <div class="hero">
        <h1>💳 Transaction Center</h1>
        <p>Add activity, filter it and understand where your money is going.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("transaction_form", clear_on_submit=True):
        a, b, c = st.columns(3)
        with a:
            d = st.date_input("Date", date.today())
            desc = st.text_input("Description", placeholder="e.g. School supplies")
        with b:
            typ = st.radio("Type", ["Expense", "Income"], horizontal=True)
            category_options = ["Income", "Food", "Transport", "Housing", "Entertainment",
                                "Shopping", "Bills", "Health", "Education", "Other"]
            category = st.selectbox("Category", category_options)
        with c:
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            add = st.form_submit_button("➕ Add transaction", type="primary", use_container_width=True)

    if add:
        if amount <= 0:
            st.warning("Enter an amount greater than zero.")
        else:
            signed = amount if typ == "Income" else -amount
            row = pd.DataFrame([{
                "Date": d,
                "Description": desc.strip() or category,
                "Category": "Income" if typ == "Income" else category,
                "Amount": signed
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, row], ignore_index=True)
            st.success("Transaction added.")
            st.rerun()

    st.divider()
    tx = st.session_state.transactions.copy()
    q = st.text_input("🔎 Search transactions", placeholder="Search description or category...")
    filtered = tx.copy()
    if q:
        mask = (
            filtered["Description"].astype(str).str.contains(q, case=False, na=False) |
            filtered["Category"].astype(str).str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]

    st.dataframe(
        filtered.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export visible transactions as CSV", csv,
                       "wallet_transactions.csv", "text/csv")

    st.markdown("### 🗑️ Remove a transaction")
    if not tx.empty:
        options = [
            f"{i}: {r['Date']} — {r['Description']} — {money(r['Amount'])}"
            for i, r in tx.iterrows()
        ]
        selected = st.selectbox("Select transaction", options)
        selected_idx = int(selected.split(":")[0])
        if st.button("Delete selected transaction"):
            st.session_state.transactions = tx.drop(index=selected_idx).reset_index(drop=True)
            st.success("Transaction deleted.")
            st.rerun()

# ----------------------------- Budget -----------------------------
elif page == "📊 Budget":
    st.markdown("""
    <div class="hero">
        <h1>📊 Budget Lab</h1>
        <p>Give every major spending category a limit and see which ones need attention.</p>
    </div>
    """, unsafe_allow_html=True)

    tx = st.session_state.transactions
    expenses = tx[tx["Amount"] < 0].copy()
    if expenses.empty:
        spent = pd.Series(dtype=float)
    else:
        expenses["Spent"] = expenses["Amount"].abs()
        spent = expenses.groupby("Category")["Spent"].sum()

    categories = list(st.session_state.budgets.keys())
    rows = []
    for cat in categories:
        current = float(spent.get(cat, 0))
        limit = float(st.session_state.budgets[cat])
        ratio = current / limit * 100 if limit else 0
        rows.append({"Category": cat, "Budget": limit, "Spent": current, "Remaining": limit-current, "Usage %": ratio})
    budget_df = pd.DataFrame(rows)

    st.dataframe(
        budget_df.style.format({"Budget": "₹{:,.0f}", "Spent": "₹{:,.0f}",
                                "Remaining": "₹{:,.0f}", "Usage %": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 🎛️ Adjust limits")
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            new_limit = st.number_input(
                cat, min_value=0.0, value=float(st.session_state.budgets[cat]),
                step=500.0, key=f"limit_{cat}"
            )
            st.session_state.budgets[cat] = new_limit
            current = float(spent.get(cat, 0))
            ratio = current / new_limit if new_limit else 0
            st.progress(min(ratio, 1))
            if new_limit and current > new_limit:
                st.error(f"Over budget by {money(current-new_limit)}")
            else:
                st.caption(f"{money(max(new_limit-current, 0))} remaining")

# ----------------------------- Goals -----------------------------
elif page == "🎯 Goals":
    st.markdown("""
    <div class="hero">
        <h1>🎯 Goal Tracker</h1>
        <p>Turn big purchases and savings targets into visible progress.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("goal_form", clear_on_submit=True):
        a, b, c, d = st.columns(4)
        with a: name = st.text_input("Goal name", placeholder="e.g. Emergency fund")
        with b: target = st.number_input("Target (₹)", min_value=0.0, step=1000.0)
        with c: saved = st.number_input("Already saved (₹)", min_value=0.0, step=1000.0)
        with d: deadline = st.date_input("Deadline", date.today() + timedelta(days=180))
        if st.form_submit_button("🎯 Add goal", type="primary", use_container_width=True):
            if not name.strip() or target <= 0:
                st.warning("Enter a goal name and a target greater than zero.")
            elif saved > target:
                st.warning("Already saved cannot be greater than the target.")
            else:
                st.session_state.goals = pd.concat([
                    st.session_state.goals,
                    pd.DataFrame([{"Goal": name.strip(), "Target": target, "Saved": saved, "Deadline": deadline}])
                ], ignore_index=True)
                st.success("Goal created!")
                st.rerun()

    st.divider()
    goals = st.session_state.goals
    if goals.empty:
        st.info("No goals yet. Create your first one above.")
    else:
        for i, g in goals.iterrows():
            progress = min(float(g["Saved"]) / float(g["Target"]), 1) if g["Target"] else 0
            remaining = max(float(g["Target"]) - float(g["Saved"]), 0)
            days_left = (pd.to_datetime(g["Deadline"]).date() - date.today()).days

            st.markdown(f"### 🎯 {g['Goal']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Progress", pct(progress * 100))
            c2.metric("Remaining", money(remaining))
            c3.metric("Deadline", f"{max(days_left, 0)} days")
            st.progress(progress)

            if progress >= 1:
                st.success("🎉 Goal reached!")
            elif days_left < 0:
                st.error("Deadline has passed — consider updating the target date.")
            else:
                monthly_needed = remaining / max(days_left / 30.44, 1)
                st.caption(f"Approx. {money(monthly_needed)}/month would be needed to reach it by the deadline.")

            if st.button("Delete this goal", key=f"delete_goal_{i}"):
                st.session_state.goals = goals.drop(index=i).reset_index(drop=True)
                st.rerun()

            st.divider()

# ----------------------------- Advisor -----------------------------
elif page == "🤖 Advisor":
    m = calculate_metrics()
    score = health_score(m)

    st.markdown("""
    <div class="hero">
        <h1>🤖 Personal Money Advisor</h1>
        <p>Educational guidance generated from the numbers in your wallet.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Wallet health", f"{score}/100")
        st.progress(score / 100)
        st.caption(health_label(score))
    with c2:
        st.markdown(f'<div class="insight"><b>Top insight</b><br>{advisor_message(m)}</div>',
                    unsafe_allow_html=True)

    st.markdown("### 🔍 What should you work on?")
    recommendations = []

    if m["balance"] < 0:
        recommendations.append("Your cash flow is negative. Focus first on bringing monthly spending below income.")
    else:
        recommendations.append(f"You have about {money(m['balance'])} of monthly cash flow after expenditure.")

    if m["savings_rate"] < 10:
        recommendations.append("Try a small, realistic automatic savings target before increasing it.")
    elif m["savings_rate"] >= 20:
        recommendations.append("Your savings rate is strong. Protect that habit while avoiding unnecessary lifestyle inflation.")

    if m["emergency_months"] < 3:
        recommendations.append("Consider building a larger emergency buffer before taking on higher-risk financial commitments.")
    else:
        recommendations.append(f"Your current savings represent roughly {m['emergency_months']:.1f} months of expenses.")

    top = top_expenses()
    if not top.empty:
        recommendations.append(f"Your largest tracked spending category is {top.index[0]} at about {money(top.iloc[0])}.")

    for r in recommendations:
        st.markdown(f'<div class="insight">💡 {r}</div>', unsafe_allow_html=True)

    st.markdown("### 💬 Ask the advisor")
    question = st.text_area(
        "Your question",
        placeholder="Examples: How can I improve my savings rate? Which expense should I review first?",
        height=110
    )

    if st.button("🧠 Analyze my question", type="primary"):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            q = question.lower()
            top = top_expenses()
            if any(word in q for word in ["save", "saving"]):
                answer = f"Your current monthly cash flow is {money(m['balance'])}. A practical starting point is to set a specific automatic savings target of a size you can consistently maintain."
            elif any(word in q for word in ["expense", "spend", "cut", "budget"]):
                biggest = top.index[0] if not top.empty else "your largest category"
                answer = f"Start by reviewing {biggest}. Compare actual spending with your budget, then look for one or two changes that are realistic to keep for several months."
            elif any(word in q for word in ["invest", "investment"]):
                answer = "Investing decisions depend on goals, time horizon and risk tolerance. Keep your emergency savings separate and research products carefully before committing money."
            elif any(word in q for word in ["goal", "laptop", "emergency"]):
                answer = "Use the Goals page to break the target into a monthly amount and track progress. Smaller milestones can make a large target easier to manage."
            else:
                answer = advisor_message(m) + " Use the Dashboard and Budget pages to explore the numbers behind this result."
            st.success(answer)

    st.caption("This advisor is educational and does not provide regulated or personalized financial advice.")

# ----------------------------- Conclusion -----------------------------
elif page == "✨ Conclusion":
    m = calculate_metrics()
    score = health_score(m)

    st.markdown("""
    <div class="hero">
        <h1>✨ Your Financial Conclusion</h1>
        <p>A single-page summary of what your current numbers are telling you.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Income", money(m["income"]))
    with c2: st.metric("Expenditure", money(m["expenses"]))
    with c3: st.metric("Monthly balance", money(m["balance"]))
    with c4: st.metric("Health score", f"{score}/100")

    st.divider()

    if m["income"] <= 0:
        st.warning("Add your income in Financial Profile to generate a meaningful conclusion.")
    elif m["balance"] < 0:
        st.error(f"⚠️ Your expenditure exceeds income by {money(abs(m['balance']))} per month.")
    elif m["savings_rate"] < 10:
        st.warning("⚠️ Your cash flow is positive, but your savings rate is currently below 10%.")
    elif m["savings_rate"] < 20:
        st.info("👍 You have positive cash flow. Increasing your savings rate gradually could strengthen your position.")
    else:
        st.success("🌟 You have a strong positive cash flow and a savings rate of at least 20%.")

    st.markdown("### 📋 Final assessment")
    assessment = [
        f"Monthly income: {money(m['income'])}",
        f"Monthly expenditure: {money(m['expenses'])}",
        f"Monthly cash flow: {money(m['balance'])}",
        f"Savings rate: {pct(m['savings_rate'])}",
        f"Current savings: {money(m['savings'])}",
        f"Current investments: {money(m['investments'])}",
        f"Estimated emergency runway: {m['emergency_months']:.1f} months",
    ]
    for item in assessment:
        st.markdown(f"- {item}")

    st.markdown("### 🚀 Your next 5 moves")
    steps = [
        "Keep monthly spending below income.",
        "Set a savings target that is realistic enough to repeat every month.",
        "Review the biggest spending category before trying to cut everything.",
        "Track goals with deadlines and update them when circumstances change.",
        "Research investments carefully and consider goals and risk tolerance before investing.",
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f'<div class="card"><b>{i}.</b> {step}</div>', unsafe_allow_html=True)

    st.markdown("### 💎 Bottom line")
    st.info(
        f"You currently have approximately {money(m['balance'])} left after monthly expenditure. "
        f"Your wallet health score is {score}/100 ({health_label(score)}). "
        "Use the Dashboard, Budget and Goals pages together to turn these numbers into a repeatable system."
    )

    st.caption("AI Wallet Advisor is an educational budgeting tool. It is not a substitute for professional financial advice.")

# ----------------------------- Footer -----------------------------
st.divider()
st.caption("💎 AI Wallet Advisor Ultimate • Built with Streamlit • Educational use only")
