"""
analytics.py
All grouping, summarisation, and business-insight computations.
Each function returns a plain pandas DataFrame ready for display or charting.
"""

import pandas as pd


# ──────────────────────────────────────────────
# 1. OVERALL KPIs
# ──────────────────────────────────────────────

def overall_kpis(df: pd.DataFrame) -> dict:
    """Return top-level KPI values."""
    return {
        "Total Transactions": len(df),
        "Total Revenue (Sales)": round(df["Calculated Sales"].sum(), 2),
        "Total Tax Collected": round(df["Tax 5%"].sum(), 2) if "Tax 5%" in df.columns else 0,
        "Total Gross Income": round(df["gross income"].sum(), 2) if "gross income" in df.columns else 0,
        "Average Sale per Transaction": round(df["Calculated Sales"].mean(), 2),
        "Average Rating": round(df["Rating"].mean(), 2) if "Rating" in df.columns else 0,
        "Average Quantity per Transaction": round(df["Quantity"].mean(), 2),
    }


# ──────────────────────────────────────────────
# 2. SALES BY PRODUCT LINE
# ──────────────────────────────────────────────

def sales_by_product_line(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales, count, avg sale, avg rating per product line."""
    grp = (
        df.groupby("Product line")
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Sale=("Calculated Sales", "mean"),
            Avg_Rating=("Rating", "mean"),
            Total_Quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp["Avg_Sale"] = grp["Avg_Sale"].round(2)
    grp["Avg_Rating"] = grp["Avg_Rating"].round(2)
    grp.columns = ["Product Line", "Total Sales ($)", "Transactions",
                   "Avg Sale ($)", "Avg Rating", "Total Qty Sold"]
    return grp


# ──────────────────────────────────────────────
# 3. SALES BY BRANCH / CITY
# ──────────────────────────────────────────────

def sales_by_branch(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby(["Branch", "City"])
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Sale=("Calculated Sales", "mean"),
            Gross_Income=("gross income", "sum"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp["Avg_Sale"] = grp["Avg_Sale"].round(2)
    grp["Gross_Income"] = grp["Gross_Income"].round(2)
    grp.columns = ["Branch", "City", "Total Sales ($)", "Transactions",
                   "Avg Sale ($)", "Gross Income ($)"]
    return grp


# ──────────────────────────────────────────────
# 4. SALES BY CUSTOMER TYPE
# ──────────────────────────────────────────────

def sales_by_customer_type(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("Customer type")
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Sale=("Calculated Sales", "mean"),
            Avg_Rating=("Rating", "mean"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp["Avg_Sale"] = grp["Avg_Sale"].round(2)
    grp["Avg_Rating"] = grp["Avg_Rating"].round(2)
    grp.columns = ["Customer Type", "Total Sales ($)", "Transactions",
                   "Avg Sale ($)", "Avg Rating"]
    return grp


# ──────────────────────────────────────────────
# 5. SALES BY GENDER
# ──────────────────────────────────────────────

def sales_by_gender(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("Gender")
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Sale=("Calculated Sales", "mean"),
        )
        .reset_index()
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp["Avg_Sale"] = grp["Avg_Sale"].round(2)
    grp.columns = ["Gender", "Total Sales ($)", "Transactions", "Avg Sale ($)"]
    return grp


# ──────────────────────────────────────────────
# 6. SALES BY PAYMENT METHOD
# ──────────────────────────────────────────────

def sales_by_payment(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("Payment")
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp.columns = ["Payment Method", "Total Sales ($)", "Transactions"]
    return grp


# ──────────────────────────────────────────────
# 7. MONTHLY SALES TREND
# ──────────────────────────────────────────────

def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    if "Month" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["Month_num", "Month"])
        .agg(
            Total_Sales=("Calculated Sales", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Sale=("Calculated Sales", "mean"),
        )
        .reset_index()
        .sort_values("Month_num")
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp["Avg_Sale"] = grp["Avg_Sale"].round(2)
    grp.columns = ["Month #", "Month", "Total Sales ($)", "Transactions", "Avg Sale ($)"]
    return grp


# ──────────────────────────────────────────────
# 8. SALES BY DAY OF WEEK
# ──────────────────────────────────────────────

def sales_by_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    if "Day of Week" not in df.columns:
        return pd.DataFrame()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grp = (
        df.groupby("Day of Week")
        .agg(Total_Sales=("Calculated Sales", "sum"), Transactions=("Invoice ID", "count"))
        .reindex(day_order)
        .dropna()
        .reset_index()
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp.columns = ["Day of Week", "Total Sales ($)", "Transactions"]
    return grp


# ──────────────────────────────────────────────
# 9. SALES BY HOUR (peak hours)
# ──────────────────────────────────────────────

def sales_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    if "Hour" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby("Hour")
        .agg(Total_Sales=("Calculated Sales", "sum"), Transactions=("Invoice ID", "count"))
        .reset_index()
        .sort_values("Hour")
    )
    grp["Total_Sales"] = grp["Total_Sales"].round(2)
    grp.columns = ["Hour", "Total Sales ($)", "Transactions"]
    return grp


# ──────────────────────────────────────────────
# 10. RATING DISTRIBUTION BY PRODUCT LINE
# ──────────────────────────────────────────────

def rating_by_product_line(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("Product line")["Rating"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
    )
    grp.columns = ["Product Line", "Avg Rating", "Min Rating", "Max Rating", "Count"]
    grp["Avg Rating"] = grp["Avg Rating"].round(2)
    return grp.sort_values("Avg Rating", ascending=False)


# ──────────────────────────────────────────────
# 11. TOP 10 TRANSACTIONS
# ──────────────────────────────────────────────

def top_transactions(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    cols = ["Invoice ID", "Branch", "City", "Product line",
            "Unit price", "Quantity", "Calculated Sales", "Rating", "Date"]
    available = [c for c in cols if c in df.columns]
    top = df[available].sort_values("Calculated Sales", ascending=False).head(n).copy()
    top["Calculated Sales"] = top["Calculated Sales"].round(2)
    top["Unit price"] = top["Unit price"].round(2)
    if "Date" in top.columns:
        top["Date"] = top["Date"].dt.strftime("%Y-%m-%d")
    top.columns = [c.replace("Calculated Sales", "Sales ($)") for c in top.columns]
    return top.reset_index(drop=True)


# ──────────────────────────────────────────────
# 12. BUSINESS INSIGHTS (text)
# ──────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[dict]:
    """
    Derive actionable business insights from the data.
    Returns a list of dicts: {icon, title, insight, recommendation}.
    """
    insights = []

    # Best product line
    pl = sales_by_product_line(df)
    best_pl = pl.iloc[0]
    worst_pl = pl.iloc[-1]
    insights.append({
        "icon": "🏆",
        "title": "Top Revenue Product Line",
        "insight": f"**{best_pl['Product Line']}** generates the highest revenue at "
                   f"**${best_pl['Total Sales ($)']:,.2f}** across {best_pl['Transactions']} transactions.",
        "recommendation": f"Increase stock and promotional spend on **{best_pl['Product Line']}**. "
                          f"Consider upselling alongside {worst_pl['Product Line']} to lift its performance.",
    })

    # Best branch
    br = sales_by_branch(df)
    best_br = br.iloc[0]
    insights.append({
        "icon": "🏬",
        "title": "Highest Performing Branch",
        "insight": f"Branch **{best_br['Branch']} ({best_br['City']})** leads with "
                   f"**${best_br['Total Sales ($)']:,.2f}** in total sales.",
        "recommendation": "Replicate the top branch's product mix, staffing model, or promotions "
                          "at lower-performing branches.",
    })

    # Customer type
    ct = sales_by_customer_type(df)
    if len(ct) >= 2:
        diff = ct.iloc[0]["Total Sales ($)"] - ct.iloc[1]["Total Sales ($)"]
        insights.append({
            "icon": "👥",
            "title": "Member vs Normal Customers",
            "insight": f"**{ct.iloc[0]['Customer Type']}** customers outspend the other group "
                       f"by **${diff:,.2f}** in total.",
            "recommendation": "Launch a loyalty rewards programme to convert Normal customers to Members "
                              "and retain existing Members with exclusive discounts.",
        })

    # Peak hour
    hr = sales_by_hour(df)
    if not hr.empty:
        peak_hr = hr.loc[hr["Total Sales ($)"].idxmax()]
        insights.append({
            "icon": "⏰",
            "title": "Peak Shopping Hour",
            "insight": f"The busiest hour is **{int(peak_hr['Hour']):02d}:00–{int(peak_hr['Hour'])+1:02d}:00** "
                       f"with **${peak_hr['Total Sales ($)']:,.2f}** in sales.",
            "recommendation": "Ensure full staffing, stocked shelves, and active promotions during peak hours. "
                              "Consider time-limited deals to drive off-peak traffic.",
        })

    # Best payment method
    pay = sales_by_payment(df)
    best_pay = pay.iloc[0]
    insights.append({
        "icon": "💳",
        "title": "Preferred Payment Method",
        "insight": f"**{best_pay['Payment Method']}** is the most-used payment method "
                   f"with **{best_pay['Transactions']}** transactions totalling **${best_pay['Total Sales ($)']:,.2f}**.",
        "recommendation": f"Partner with {best_pay['Payment Method']} providers for cashback offers "
                          "to increase basket size.",
    })

    # Rating insight
    rt = rating_by_product_line(df)
    best_rated = rt.iloc[0]
    worst_rated = rt.iloc[-1]
    insights.append({
        "icon": "⭐",
        "title": "Customer Satisfaction Insight",
        "insight": f"**{best_rated['Product Line']}** has the highest average rating of "
                   f"**{best_rated['Avg Rating']}**, while "
                   f"**{worst_rated['Product Line']}** scores lowest at **{worst_rated['Avg Rating']}**.",
        "recommendation": f"Investigate quality or service issues in **{worst_rated['Product Line']}** "
                          "through customer feedback surveys and supplier audits.",
    })

    return insights
