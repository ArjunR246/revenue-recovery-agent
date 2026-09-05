import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Revenue Recovery Agent",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI Revenue Recovery Agent")
st.caption("Razorpay Buildathon Submission")

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return None


ai_metrics = load_csv("data/ai_metrics.csv")
baseline_metrics = load_csv("data/baseline_metrics.csv")
audit_logs = load_csv("data/audit_logs.csv")
executed = load_csv("data/executed_interventions.csv")
stopping = load_csv("data/stopping_rule_results.csv")
routing = load_csv("data/routing_decisions.csv")
baseline_results = load_csv("data/baseline_results.csv")

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "Agent Behavior",
        "Recovery Decay Model",
        "Audit Trail"
    ]
)

# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with tab1:

    st.header("📊 Headline Metrics")

    try:

        ai = ai_metrics.iloc[0]

        contacted = audit_logs[
            audit_logs["simulated_outcome"]
            !=
            "NOT_CONTACTED"
        ]

        contacted_recovery_rate = (
            (
                contacted["simulated_outcome"]
                ==
                "RECOVERED"
            ).mean()
            * 100
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "At-Risk Revenue",
            f"₹{ai['at_risk_revenue']:,.0f}"
        )

        c2.metric(
            "Recovered Revenue",
            f"₹{ai['recovered_revenue']:,.0f}"
        )

        c3.metric(
            "Overall Recovery Rate",
            f"{ai['recovery_rate'] * 100:.2f}%"
        )

        c4.metric(
            "Contacted Recovery Rate",
            f"{contacted_recovery_rate:.2f}%"
        )

        c5.metric(
            "Checkouts Processed",
            f"{int(ai['total_checkouts']):,}"
        )

    except Exception as e:
        st.error(f"KPI section failed: {e}")

    st.divider()

    st.header("🚀 AI Agent vs Baseline")

    try:

        ai = ai_metrics.iloc[0]
        baseline = baseline_metrics.iloc[0]

        # ==================================================
        # Efficiency Metrics
        # ==================================================

        ai_contacted = len(
            audit_logs[
                audit_logs["simulated_outcome"]
                != "NOT_CONTACTED"
            ]
        )

        ai_recoveries = len(
            audit_logs[
                audit_logs["simulated_outcome"]
                == "RECOVERED"
            ]
        )

        ai_wasted_rate = (
            len(
                audit_logs[
                    audit_logs["simulated_outcome"]
                    == "PENDING"
                ]
            )
            /
            ai_contacted
        )

        baseline_contacted = len(
            baseline_results
        )

        baseline_recoveries = len(
            baseline_results[
                baseline_results["outcome"]
                == "RECOVERED"
            ]
        )

        baseline_wasted_rate = (
            len(
                baseline_results[
                    baseline_results["outcome"]
                    == "PENDING"
                ]
            )
            /
            baseline_contacted
        )

        comparison = pd.DataFrame({
            "Metric": [
                "Recovered Revenue",
                "Recovery Rate",
                "Touches per Recovery",
                "Contact Rate",
                "Wasted Contact Rate"
            ],

            "AI Agent": [
                f"₹{ai['recovered_revenue']:,.0f}",
                f"{ai['recovery_rate'] * 100:.2f}%",
                f"{ai['touches_per_recovery']:.2f}",
                f"{100 * ai_contacted / ai['total_checkouts']:.1f}%",
                f"{100 * ai_wasted_rate:.1f}%"
            ],

            "Baseline": [
                f"₹{baseline['recovered_revenue']:,.0f}",
                f"{baseline['recovery_rate']:.2f}%",
                f"{baseline['touches_per_recovery']:.2f}",
                "100.0%",
                f"{100 * baseline_wasted_rate:.1f}%"
            ]
        })

        st.table(comparison)

        chart_df = pd.DataFrame({
            "Strategy": [
                "AI Agent",
                "Baseline"
            ],
            "Recovered Revenue": [
                ai["recovered_revenue"],
                baseline["recovered_revenue"]
            ]
        })

        fig = px.bar(
            chart_df,
            x="Strategy",
            y="Recovered Revenue",
            title="Recovered Revenue Comparison"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "Baseline contacts every abandoned checkout with a generic reminder. "
            "The AI Agent selectively intervenes only when expected value justifies action, "
            "reducing unnecessary contacts through recoverability modeling and stopping rules."
        )

    except Exception as e:
        st.error(f"Comparison section failed: {e}")

# ============================================================
# TAB 2 - AGENT BEHAVIOR
# ============================================================

with tab2:

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # ACTION DISTRIBUTION
    # --------------------------------------------------------

    with col1:

        try:

            st.subheader("⚡ Action Distribution")

            action_counts = (
                routing["chosen_action"]
                .value_counts()
                .reset_index()
            )

            action_counts.columns = [
                "Action",
                "Count"
            ]

            fig = px.bar(
                action_counts,
                x="Action",
                y="Count"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(e)

    # --------------------------------------------------------
    # RECOVERY BY ROOT CAUSE
    # --------------------------------------------------------

    with col2:

        try:

            st.subheader("🧠 Recovery by Root Cause")

            recovered = audit_logs[
                audit_logs["simulated_outcome"]
                ==
                "RECOVERED"
            ]

            cause_counts = (
                recovered["predicted_cause"]
                .value_counts()
                .reset_index()
            )

            cause_counts.columns = [
                "Root Cause",
                "Recovered"
            ]

            fig = px.bar(
                cause_counts,
                x="Root Cause",
                y="Recovered"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(e)

    # --------------------------------------------------------
    # STOP REASONS
    # --------------------------------------------------------

    with col3:

        try:

            st.subheader(
                "🛑 Why the Agent Chose NOT to Act"
            )

            stop_counts = (
                stopping["stop_reason"]
                .value_counts()
                .reset_index()
            )

            stop_counts.columns = [
                "Reason",
                "Count"
            ]

            fig = px.pie(
                stop_counts,
                names="Reason",
                values="Count"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(e)

# ============================================================
# TAB 3 - DECAY MODEL
# ============================================================

with tab3:

    st.header("📉 Recovery Decay Model")

    st.markdown(
        """
        The agent models recoverability as an exponential decay function.
        Different abandonment causes decay at different rates, allowing
        intervention timing to be optimized for each root cause.
        """
    )

    t = np.linspace(
        0,
        4320,
        500
    )

    params = {
        "OTP_FRICTION":
            (0.2424, 0.001232, 0.3635),

        "PAYMENT_FAILURE":
            (0.1862, 0.001026, 0.2977),

        "DISTRACTION_TIMEOUT":
            (0.2324, 0.001017, 0.2100),

        "PRICE_HESITATION":
            (0.1292, 0.000375, 0.1080)
    }

    fig = go.Figure()

    for cause, (A, k, C) in params.items():

        y = (
            A
            *
            np.exp(-k * t)
            +
            C
        )

        fig.add_trace(
            go.Scatter(
                x=t,
                y=y,
                mode="lines",
                name=cause
            )
        )

    fig.update_layout(
        title="Recoverability Decay by Root Cause",
        xaxis_title="Minutes Since Dropoff",
        yaxis_title="Recovery Probability",
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Notice how PRICE_HESITATION decays much slower than the other causes — customers still hesitating on price remain recoverable far longer than those experiencing technical friction."
    )

# ============================================================
# TAB 4 - AUDIT TRAIL
# ============================================================

with tab4:

    st.header("🔍 Audit Trail")

    try:

        search = st.text_input(
            "Search Checkout ID"
        )

        action_filter = st.selectbox(
            "Filter by Action",
            ["All"]
            +
            sorted(
                audit_logs[
                    "chosen_action"
                ]
                .dropna()
                .unique()
                .tolist()
            )
        )

        cause_filter = st.selectbox(
            "Filter by Cause",
            ["All"]
            +
            sorted(
                audit_logs[
                    "predicted_cause"
                ]
                .dropna()
                .unique()
                .tolist()
            )
        )

        filtered = audit_logs.copy()

        if search:

            filtered = filtered[
                filtered["checkout_id"]
                .astype(str)
                .str.contains(
                    search,
                    case=False
                )
            ]

        if action_filter != "All":

            filtered = filtered[
                filtered["chosen_action"]
                ==
                action_filter
            ]

        if cause_filter != "All":

            filtered = filtered[
                filtered["predicted_cause"]
                ==
                cause_filter
            ]

        st.dataframe(
            filtered,
            height=600,
            use_container_width=True
        )

    except Exception as e:
        st.error(
            f"Audit trail failed: {e}"
        )