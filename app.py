"""
app.py  –  Supermarket Sales Analytics Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

# ── Path setup ──────────────────────────────────────────────────────────────
THIS_DIR = Path(__file__).parent
ROOT_DIR = THIS_DIR                 # workspace root where the CSV lives
sys.path.insert(0, str(THIS_DIR))

from data_loader import load_data, validate_columns, audit_data_quality, clean_data
import analytics as an

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supermarket Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette ─────────────────────────────────────────────────────────────
PALETTE = px.colors.qualitative.Set2
ACCENT  = "#3b82d4"

# ── Global Plotly layout defaults (black text, white background) ──────────────
import plotly.io as pio
pio.templates["supermarket"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="-apple-system, Segoe UI, system-ui, sans-serif", color="#000000", size=13),
        title=dict(font=dict(color="#000000", size=15)),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        xaxis=dict(
            tickfont=dict(color="#000000", size=12),
            title=dict(font=dict(color="#000000", size=13)),
            gridcolor="#e5e7eb",
            linecolor="#cccccc",
            color="#000000",
        ),
        yaxis=dict(
            tickfont=dict(color="#000000", size=12),
            title=dict(font=dict(color="#000000", size=13)),
            gridcolor="#e5e7eb",
            linecolor="#cccccc",
            color="#000000",
        ),
        legend=dict(font=dict(color="#000000", size=12)),
        coloraxis=dict(colorbar=dict(tickfont=dict(color="#000000"),
                                     title=dict(font=dict(color="#000000")))),
    )
)
pio.templates.default = "plotly+supermarket"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── force white background everywhere ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"],
[data-testid="block-container"],
section[data-testid="stSidebar"] > div,
.stTabs, .stTab, [data-baseweb="tab-panel"],
[data-testid="stVerticalBlock"] {
    background-color: #ffffff !important;
}

/* ── global text ── */
html, body, [class*="css"] {
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    font-size: 15px;
    color: #000000;
    line-height: 1.6;
    background-color: #ffffff;
}

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 10px;
    padding: 20px 16px 16px 16px;
    text-align: center;
    margin-bottom: 4px;
}
.kpi-label { font-size: 13px; font-weight: 700; color: #000000; letter-spacing: .3px; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #000000; }
.kpi-sub   { font-size: 12px; font-weight: 500; color: #000000; margin-top: 4px; }

/* ── insight cards ── */
.insight-card {
    background: #ffffff;
    border: 1.5px solid #000000;
    border-left: 5px solid #000000;
    border-radius: 6px;
    padding: 16px 18px;
    margin-bottom: 14px;
}
.insight-title { font-weight: 800; font-size: 16px; color: #000000; margin-bottom: 6px; }
.insight-body  { font-size: 14.5px; font-weight: 400; color: #000000; margin-bottom: 8px; line-height: 1.6; }
.insight-rec   {
    font-size: 14px; font-weight: 500; color: #000000;
    background: #f0f0f0; border-radius: 4px;
    padding: 10px 12px; margin-top: 6px; line-height: 1.6;
    border-left: 3px solid #000000;
}

/* ── section headers ── */
.section-header {
    font-size: 19px; font-weight: 800; color: #000000;
    border-bottom: 2px solid #000000;
    padding-bottom: 7px; margin-top: 10px; margin-bottom: 18px;
}

/* ── sidebar title ── */
.sidebar-title { font-size: 16px; font-weight: 700; color: #000000; margin-bottom: 4px; }

/* ── tab labels ── */
button[data-baseweb="tab"] { font-size: 14px !important; font-weight: 600 !important; color: #000000 !important; }

/* ── all text elements ── */
p, li, span, label, div, h1, h2, h3, h4, h5, h6 { color: #000000; }
.stMarkdown p { font-size: 15px; font-weight: 400; color: #000000; }

/* ── metrics / st.metric ── */
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color: #000000 !important; }

/* ── dataframe cells ── */
[data-testid="stDataFrame"] * { color: #000000 !important; }

/* ── sidebar text ── */
[data-testid="stSidebar"] * { color: #000000 !important; background-color: #ffffff !important; }
[data-testid="stSidebar"] .stMultiSelect span,
[data-testid="stSidebar"] label { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DATA LOADING  (cached so it only runs once per session)
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading dataset …")
def get_data(csv_path: str):
    raw   = load_data(csv_path)
    clean, log = clean_data(raw)
    return raw, clean, log


CSV_PATH = str(ROOT_DIR / "SuperMarket Analysis.csv")

try:
    raw_df, df, clean_log = get_data(CSV_PATH)
except FileNotFoundError as e:
    st.error(f"❌  Dataset not found: {e}\n\nMake sure **SuperMarket Analysis.csv** is in the workspace root.")
    st.stop()


# ══════════════════════════════════════════════════════════════
# SIDEBAR – Filters
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shopping-cart--v2.png", width=56)
    st.markdown("## 🛒 Supermarket Analytics")
    st.markdown("---")

    st.markdown('<p class="sidebar-title">🔍 Filters</p>', unsafe_allow_html=True)

    branches   = sorted(df["Branch"].dropna().unique().tolist())
    sel_branch = st.multiselect("Branch", branches, default=branches)

    cities   = sorted(df["City"].dropna().unique().tolist())
    sel_city = st.multiselect("City", cities, default=cities)

    product_lines = sorted(df["Product line"].dropna().unique().tolist())
    sel_pl = st.multiselect("Product Line", product_lines, default=product_lines)

    customer_types = sorted(df["Customer type"].dropna().unique().tolist())
    sel_ct = st.multiselect("Customer Type", customer_types, default=customer_types)

    payments = sorted(df["Payment"].dropna().unique().tolist())
    sel_pay  = st.multiselect("Payment Method", payments, default=payments)

    st.markdown("---")
    st.markdown(
        f"**Dataset:** {len(df):,} rows · {len(df.columns)} columns",
        help="After cleaning.",
    )

# Apply filters
mask = (
    df["Branch"].isin(sel_branch) &
    df["City"].isin(sel_city) &
    df["Product line"].isin(sel_pl) &
    df["Customer type"].isin(sel_ct) &
    df["Payment"].isin(sel_pay)
)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data matches the selected filters. Please broaden your selection.")
    st.stop()


# ══════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════
tab_overview, tab_products, tab_branches, tab_customers, tab_time, tab_data_quality, tab_insights = st.tabs([
    "📊 Overview",
    "🛍️ Products",
    "🏬 Branches",
    "👥 Customers",
    "📅 Time Trends",
    "🔎 Data Quality",
    "💡 Business Insights",
])


# ─────────────────────────────────────────────
# TAB 1 – OVERVIEW
# ─────────────────────────────────────────────
with tab_overview:
    st.markdown('<div class="section-header">Overall Performance KPIs</div>', unsafe_allow_html=True)

    kpis = an.overall_kpis(fdf)
    kpi_items = list(kpis.items())
    cols = st.columns(4)
    for i, (label, value) in enumerate(kpi_items):
        col = cols[i % 4]
        if isinstance(value, float):
            display = f"${value:,.2f}" if "Revenue" in label or "Sale" in label or "Tax" in label or "Income" in label else f"{value:,.2f}"
        else:
            display = f"{value:,}"
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label.upper()}</div>
                <div class="kpi-value">{display}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sales distribution overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Sales by Product Line</div>', unsafe_allow_html=True)
        pl_df = an.sales_by_product_line(fdf)
        fig = px.bar(
            pl_df, x="Total Sales ($)", y="Product Line",
            orientation="h", color="Product Line",
            color_discrete_sequence=PALETTE,
            text="Total Sales ($)", text_auto=".2s",
        )
        fig.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig.update_layout(
            showlegend=False, height=340,
            margin=dict(l=10, r=30, t=10, b=10),
            xaxis_title="Total Sales ($)", yaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Revenue Share by Product Line</div>', unsafe_allow_html=True)
        fig2 = px.pie(
            pl_df, names="Product Line", values="Total Sales ($)",
            color_discrete_sequence=PALETTE, hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label", textfont_size=13, textfont_color="#000000")
        fig2.update_layout(
            height=340, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly trend overview
    st.markdown('<div class="section-header">Monthly Sales Trend</div>', unsafe_allow_html=True)
    mo_df = an.monthly_sales_trend(fdf)
    if not mo_df.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=mo_df["Month"], y=mo_df["Total Sales ($)"],
            name="Total Sales", marker_color=ACCENT, opacity=0.85,
        ))
        fig3.add_trace(go.Scatter(
            x=mo_df["Month"], y=mo_df["Avg Sale ($)"],
            name="Avg Sale / Transaction", mode="lines+markers",
            line=dict(color="#7c5cd8", width=2), yaxis="y2",
        ))
        fig3.update_layout(
            yaxis=dict(title="Total Sales ($)", color="#000000"),
            yaxis2=dict(title="Avg Sale ($)", overlaying="y", side="right", color="#000000"),
            height=320, margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 2 – PRODUCTS
# ─────────────────────────────────────────────
with tab_products:
    st.markdown('<div class="section-header">Product Line Deep Dive</div>', unsafe_allow_html=True)

    pl_df = an.sales_by_product_line(fdf)

    col1, col2 = st.columns(2)
    with col1:
        # Avg sale per transaction by product line
        fig = px.bar(
            pl_df.sort_values("Avg Sale ($)"), x="Avg Sale ($)", y="Product Line",
            orientation="h", color="Product Line",
            color_discrete_sequence=PALETTE, text="Avg Sale ($)", text_auto=".2f",
            title="Average Sale per Transaction ($)",
        )
        fig.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig.update_layout(
            showlegend=False, height=340,
            margin=dict(l=10, r=30, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Total quantity sold
        fig2 = px.bar(
            pl_df.sort_values("Total Qty Sold"), x="Total Qty Sold", y="Product Line",
            orientation="h", color="Product Line",
            color_discrete_sequence=PALETTE, text="Total Qty Sold",
            title="Total Quantity Sold by Product Line",
        )
        fig2.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig2.update_layout(
            showlegend=False, height=340,
            margin=dict(l=10, r=30, t=40, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Rating by product line
    st.markdown('<div class="section-header">Customer Ratings by Product Line</div>', unsafe_allow_html=True)
    rt_df = an.rating_by_product_line(fdf)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(
            rt_df.sort_values("Avg Rating"), x="Avg Rating", y="Product Line",
            orientation="h", color="Avg Rating",
            color_continuous_scale="Blues",
            text="Avg Rating", text_auto=".2f",
            title="Average Customer Rating (out of 10)",
        )
        fig3.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig3.update_layout(
            height=340, margin=dict(l=10, r=30, t=40, b=10),
            xaxis_range=[0, 11],
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.box(
            fdf, x="Product line", y="Rating",
            color="Product line", color_discrete_sequence=PALETTE,
            title="Rating Distribution (Box Plot)",
        )
        fig4.update_layout(
            showlegend=False, height=340,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Summary table
    st.markdown('<div class="section-header">Product Line Summary Table</div>', unsafe_allow_html=True)
    st.dataframe(
        pl_df.style
            .format({"Total Sales ($)": "${:,.2f}", "Avg Sale ($)": "${:,.2f}", "Avg Rating": "{:.2f}"})
            .background_gradient(subset=["Total Sales ($)"], cmap="Blues")
            .set_properties(**{"font-size": "13px"}),
        use_container_width=True, hide_index=True,
    )


# ─────────────────────────────────────────────
# TAB 3 – BRANCHES
# ─────────────────────────────────────────────
with tab_branches:
    st.markdown('<div class="section-header">Branch & City Performance</div>', unsafe_allow_html=True)

    br_df = an.sales_by_branch(fdf)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            br_df, x="Branch", y="Total Sales ($)",
            color="City", color_discrete_sequence=PALETTE,
            text="Total Sales ($)", text_auto=".2s",
            title="Total Sales by Branch",
        )
        fig.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig.update_layout(
            height=360, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            br_df, x="Branch", y="Gross Income ($)",
            color="City", color_discrete_sequence=PALETTE,
            text="Gross Income ($)", text_auto=".2s",
            title="Gross Income by Branch",
        )
        fig2.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
        fig2.update_layout(
            height=360, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Product mix per branch
    st.markdown('<div class="section-header">Product Line Revenue per Branch</div>', unsafe_allow_html=True)
    br_pl = (
        fdf.groupby(["Branch", "Product line"])["Calculated Sales"]
        .sum().reset_index()
    )
    br_pl.columns = ["Branch", "Product Line", "Total Sales ($)"]
    fig3 = px.bar(
        br_pl, x="Branch", y="Total Sales ($)",
        color="Product Line", barmode="group",
        color_discrete_sequence=PALETTE,
        title="Revenue Breakdown by Branch and Product Line",
    )
    fig3.update_layout(
        height=380, margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Summary table
    st.markdown('<div class="section-header">Branch Summary Table</div>', unsafe_allow_html=True)
    st.dataframe(
        br_df.style
            .format({"Total Sales ($)": "${:,.2f}", "Avg Sale ($)": "${:,.2f}", "Gross Income ($)": "${:,.2f}"})
            .background_gradient(subset=["Total Sales ($)"], cmap="Greens")
            .set_properties(**{"font-size": "13px"}),
        use_container_width=True, hide_index=True,
    )


# ─────────────────────────────────────────────
# TAB 4 – CUSTOMERS
# ─────────────────────────────────────────────
with tab_customers:
    st.markdown('<div class="section-header">Customer Segmentation Analysis</div>', unsafe_allow_html=True)

    ct_df  = an.sales_by_customer_type(fdf)
    gen_df = an.sales_by_gender(fdf)
    pay_df = an.sales_by_payment(fdf)

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.pie(
            ct_df, names="Customer Type", values="Total Sales ($)",
            color_discrete_sequence=PALETTE, hole=0.4,
            title="Sales Share: Member vs Normal",
        )
        fig.update_traces(textinfo="percent+label", textfont_size=13, textfont_color="#000000")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            gen_df, names="Gender", values="Total Sales ($)",
            color_discrete_sequence=PALETTE, hole=0.4,
            title="Sales Share by Gender",
        )
        fig2.update_traces(textinfo="percent+label", textfont_size=13, textfont_color="#000000")
        fig2.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.pie(
            pay_df, names="Payment Method", values="Transactions",
            color_discrete_sequence=PALETTE, hole=0.4,
            title="Transaction Share by Payment Method",
        )
        fig3.update_traces(textinfo="percent+label", textfont_size=13, textfont_color="#000000")
        fig3.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    # Customer type × Product line heatmap
    st.markdown('<div class="section-header">Spending Heatmap: Customer Type × Product Line</div>', unsafe_allow_html=True)
    heat_df = (
        fdf.groupby(["Customer type", "Product line"])["Calculated Sales"]
        .sum().unstack(fill_value=0).round(2)
    )
    fig_heat = px.imshow(
        heat_df, text_auto=".0f", aspect="auto",
        color_continuous_scale="Blues",
        title="Total Sales Heatmap ($)",
    )
    fig_heat.update_layout(
        height=280, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_tickangle=-30,
    )
    fig_heat.update_traces(textfont_color="#000000", textfont_size=13)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Rating by gender × customer type
    st.markdown('<div class="section-header">Average Rating: Gender × Customer Type</div>', unsafe_allow_html=True)
    rt_gen = (
        fdf.groupby(["Gender", "Customer type"])["Rating"]
        .mean().reset_index()
    )
    rt_gen.columns = ["Gender", "Customer Type", "Avg Rating"]
    rt_gen["Avg Rating"] = rt_gen["Avg Rating"].round(2)
    fig_rg = px.bar(
        rt_gen, x="Customer Type", y="Avg Rating",
        color="Gender", barmode="group",
        color_discrete_sequence=PALETTE,
        text="Avg Rating", text_auto=".2f",
        title="Average Rating by Gender and Customer Type",
    )
    fig_rg.update_traces(textfont_color="#000000", textfont_size=13)
    fig_rg.update_layout(
        height=320, margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_rg, use_container_width=True)

    # Summary tables
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("**Customer Type Summary**")
        st.dataframe(
            ct_df.style
                .format({"Total Sales ($)": "${:,.2f}", "Avg Sale ($)": "${:,.2f}", "Avg Rating": "{:.2f}"})
                .set_properties(**{"font-size": "13px"}),
            use_container_width=True, hide_index=True,
        )
    with col5:
        st.markdown("**Payment Method Summary**")
        st.dataframe(
            pay_df.style
                .format({"Total Sales ($)": "${:,.2f}"})
                .set_properties(**{"font-size": "13px"}),
            use_container_width=True, hide_index=True,
        )


# ─────────────────────────────────────────────
# TAB 5 – TIME TRENDS
# ─────────────────────────────────────────────
with tab_time:
    st.markdown('<div class="section-header">Time-Based Sales Analysis</div>', unsafe_allow_html=True)

    mo_df  = an.monthly_sales_trend(fdf)
    dow_df = an.sales_by_day_of_week(fdf)
    hr_df  = an.sales_by_hour(fdf)

    # Monthly
    if not mo_df.empty:
        fig = px.line(
            mo_df, x="Month", y="Total Sales ($)",
            markers=True, line_shape="spline",
            color_discrete_sequence=[ACCENT],
            title="Monthly Revenue Trend",
        )
        fig.update_traces(line_width=2.5, marker_size=8)
        fig.update_layout(
            height=320, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if not dow_df.empty:
            fig2 = px.bar(
                dow_df, x="Day of Week", y="Total Sales ($)",
                color="Total Sales ($)", color_continuous_scale="Blues",
                text="Total Sales ($)", text_auto=".2s",
                title="Sales by Day of Week",
            )
            fig2.update_traces(textposition="outside", textfont_size=13, textfont_color="#000000")
            fig2.update_layout(
                height=360, margin=dict(l=10, r=10, t=40, b=10),
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if not hr_df.empty:
            fig3 = px.area(
                hr_df, x="Hour", y="Total Sales ($)",
                color_discrete_sequence=[ACCENT],
                title="Sales by Hour of Day (Peak Hour Analysis)",
            )
            fig3.update_traces(line_width=2)
            fig3.update_layout(
                height=360, margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(tickmode="linear", tick0=0, dtick=1),
            )
            st.plotly_chart(fig3, use_container_width=True)

    # Monthly table
    if not mo_df.empty:
        st.markdown('<div class="section-header">Monthly Summary Table</div>', unsafe_allow_html=True)
        display_mo = mo_df.drop(columns=["Month #"]).copy()
        st.dataframe(
            display_mo.style
                .format({"Total Sales ($)": "${:,.2f}", "Avg Sale ($)": "${:,.2f}"})
                .background_gradient(subset=["Total Sales ($)"], cmap="YlOrBr")
                .set_properties(**{"font-size": "13px"}),
            use_container_width=True, hide_index=True,
        )


# ─────────────────────────────────────────────
# TAB 6 – DATA QUALITY
# ─────────────────────────────────────────────
with tab_data_quality:
    st.markdown('<div class="section-header">Data Quality Audit</div>', unsafe_allow_html=True)

    # Column validation
    col_check = validate_columns(raw_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Columns (raw)", len(raw_df.columns))
    with col2:
        st.metric("Expected Columns Found", len(col_check["present"]))
    with col3:
        st.metric("Missing Expected Columns", len(col_check["missing"]))

    if col_check["missing"]:
        st.warning(f"Missing columns: {', '.join(col_check['missing'])}")
    else:
        st.success("✅  All expected columns are present in the dataset.")

    # Cleaning summary
    st.markdown('<div class="section-header">Cleaning Summary</div>', unsafe_allow_html=True)
    clean_summary = {
        "Original Rows (raw)": len(raw_df),
        "Duplicate Rows Dropped": clean_log.get("duplicate_rows_dropped", 0),
        "Final Rows (clean)": clean_log.get("final_rows", len(df)),
        "Sales Column Recalculated": "✅ Yes" if clean_log.get("sales_recalculated") else "❌ No",
    }
    clean_df_display = pd.DataFrame(list(clean_summary.items()), columns=["Metric", "Value"])
    st.dataframe(clean_df_display.style.set_properties(**{"font-size": "13px"}),
                 use_container_width=True, hide_index=True)

    # Per-column audit
    st.markdown('<div class="section-header">Per-Column Quality Report</div>', unsafe_allow_html=True)
    audit = audit_data_quality(raw_df)
    styled = (
        audit.style
        .map(lambda v: "color: #d73a49; font-weight:bold" if isinstance(v, (int, float)) and v > 0 else "",
             subset=["Missing Count"])
        .format({"Missing %": "{:.2f}%"})
        .set_properties(**{"font-size": "13px"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Calculated vs original Sales comparison
    st.markdown('<div class="section-header">Sales Recalculation Verification (Quantity × Unit Price)</div>',
                unsafe_allow_html=True)
    verify_df = df[["Invoice ID", "Quantity", "Unit price", "Sales", "Calculated Sales"]].head(20).copy()
    verify_df["Match?"] = (abs(verify_df["Calculated Sales"] - verify_df["Sales"]) < 0.01).map(
        {True: "✅ Match", False: "⚠️ Differ"}
    )
    st.dataframe(
        verify_df.style
            .format({"Unit price": "${:,.2f}", "Sales": "${:,.2f}", "Calculated Sales": "${:,.2f}"})
            .set_properties(**{"font-size": "13px"}),
        use_container_width=True, hide_index=True,
    )

    # Raw data preview
    st.markdown('<div class="section-header">Raw Dataset Preview (first 50 rows)</div>', unsafe_allow_html=True)
    st.dataframe(raw_df.head(50), use_container_width=True, height=320)


# ─────────────────────────────────────────────
# TAB 7 – BUSINESS INSIGHTS
# ─────────────────────────────────────────────
with tab_insights:
    st.markdown('<div class="section-header">Data-Driven Business Insights & Recommendations</div>',
                unsafe_allow_html=True)
    st.markdown(
        "_Insights are automatically computed from the filtered dataset. "
        "Adjust sidebar filters to explore segment-specific recommendations._"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    insights = an.generate_insights(fdf)
    for item in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{item['icon']} &nbsp; {item['title']}</div>
            <div class="insight-body">{item['insight']}</div>
            <div class="insight-rec">💼 <strong>Recommendation:</strong> {item['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Top 10 transactions
    st.markdown('<div class="section-header">Top 10 Highest-Value Transactions</div>', unsafe_allow_html=True)
    top10 = an.top_transactions(fdf, n=10)
    st.dataframe(
        top10.style
            .format({"Sales ($)": "${:,.2f}", "Unit price": "${:,.2f}"})
            .background_gradient(subset=["Sales ($)"], cmap="YlGn")
            .set_properties(**{"font-size": "13px"}),
        use_container_width=True, hide_index=True,
    )

    # Combined scatter: Unit Price vs Sales coloured by Product Line
    st.markdown('<div class="section-header">Unit Price vs Sales by Product Line</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(
        fdf, x="Unit price", y="Calculated Sales",
        color="Product line", size="Quantity",
        color_discrete_sequence=PALETTE,
        hover_data=["Invoice ID", "Branch", "Rating"],
        opacity=0.7,
        title="Unit Price vs Calculated Sales  (bubble size = Quantity)",
    )
    fig_sc.update_layout(
        height=420, margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_sc, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border:none;border-top:1px solid #e5e7eb;margin-top:32px">
<p style="text-align:center;font-size:12px;color:#57606a;margin:8px 0 4px">
    🛒 Supermarket Sales Analytics Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly
</p>
""", unsafe_allow_html=True)
