import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. WEBSITE DESIGN
# ==========================================

st.markdown("""
<style>

/* Main website */
.stApp {
    background-color: #F4F7FC;
    color: #183153;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #17365D;
    min-width: 250px;
    max-width: 250px;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Main headings */
h1 {
    color: #17365D !important;
    font-weight: 800 !important;
}

h2 {
    color: #1769AA !important;
    font-weight: 750 !important;
}

h3 {
    color: #315783 !important;
    font-weight: 700 !important;
}

/* Main title container */
.title-box {
    background: linear-gradient(110deg, #12345B, #1769AA);
    padding: 24px;
    border-radius: 14px;
    margin-bottom: 22px;
}

.title-box h1 {
    color: white !important;
    font-size: 27px !important;
    margin: 0;
}

.title-box p {
    color: #E5F0FF !important;
    margin-top: 8px;
    margin-bottom: 0;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px 16px;
    border: 1px solid #DCE6F2;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(20, 50, 90, 0.06);
    min-height: 115px;
}

[data-testid="stMetricLabel"] {
    color: #60758F !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #174A83 !important;
    font-weight: 800 !important;
}

/* Charts */
div[data-testid="stPlotlyChart"] {
    background-color: white;
    border: 1px solid #DFE8F3;
    border-radius: 12px;
    padding: 8px;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background-color: white !important;
    border-color: #C9D8EA !important;
}

/* Download button */
.stDownloadButton button {
    background-color: #1769AA !important;
    color: white !important;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

/* Footer */
.footer {
    text-align: center;
    color: #718096;
    padding: 20px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD DATA
# ==========================================


# ==========================================
# 3. LOAD DATA
# ==========================================


@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    data_file = base_dir / "cleaned_ecommerce.csv"

    df = pd.read_csv(data_file)

    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    df["total_sales"] = pd.to_numeric(
        df["total_sales"], errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"], errors="coerce"
    )

    df = df.dropna(
        subset=["order_date", "total_sales", "quantity"]
    )

    df["month"] = df["order_date"].dt.strftime("%b %Y")

    return df





# ==========================================
# 4. SIDEBAR
# ==========================================

st.sidebar.title("🛍️ E-Commerce")
st.sidebar.markdown("### Dashboard Menu")
st.sidebar.divider()

st.sidebar.markdown("### Filter Sales Data")

cities = ["All Cities"] + sorted(
    df["city"].dropna().unique().tolist()
)

categories = ["All Categories"] + sorted(
    df["category"].dropna().unique().tolist()
)

months = sorted(
    df["month"].dropna().unique().tolist(),
    key=lambda x: pd.to_datetime(x, format="%b %Y")
)

month_options = ["All Months"] + months

selected_city = st.sidebar.selectbox(
    "Choose City",
    cities
)

selected_category = st.sidebar.selectbox(
    "Choose Category",
    categories
)

selected_month = st.sidebar.selectbox(
    "Choose Month",
    month_options
)

st.sidebar.divider()
st.sidebar.caption("E-Commerce Sales Analytics")


# ==========================================
# 5. FILTER DATA
# ==========================================

data = df.copy()

if selected_city != "All Cities":
    data = data[data["city"] == selected_city]

if selected_category != "All Categories":
    data = data[data["category"] == selected_category]

if selected_month != "All Months":
    data = data[data["month"] == selected_month]


# ==========================================
# 6. MAIN DASHBOARD HEADER
# ==========================================

st.markdown("""
<div class="title-box">
    <h1>🛍️ E-Commerce Analytics Dashboard</h1>
    <p>Sales Performance | Revenue Insights | Product Analysis</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 7. CALCULATE BUSINESS METRICS
# ==========================================

revenue = data["total_sales"].sum()

orders = data["order_id"].nunique()

quantity = data["quantity"].sum()

customers = data["customer"].nunique()

products = data["product"].nunique()

order_values = data.groupby("order_id")["total_sales"].sum()

average_order = (
    order_values.mean() if not order_values.empty else 0
)


# ==========================================
# 8. BUSINESS OVERVIEW
# ==========================================

st.header("📊 Business Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Revenue",
        f"₹{revenue:,.0f}"
    )

with c2:
    st.metric(
        "Total Orders",
        f"{orders:,}"
    )

with c3:
    st.metric(
        "Average Order Value",
        f"₹{average_order:,.0f}"
    )

with c4:
    st.metric(
        "Items Sold",
        f"{quantity:,.0f}"
    )

c5, c6 = st.columns(2)

with c5:
    st.metric("Total Customers", f"{customers:,}")

with c6:
    st.metric("Total Products", f"{products:,}")


st.divider()


# ==========================================
# 9. CHART DESIGN FUNCTION
# ==========================================

def make_chart(fig, height=350):

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=12,
            color="#294766"
        ),
        height=height,
        margin=dict(l=25, r=25, t=35, b=30),
        coloraxis_showscale=False
    )

    fig.update_xaxes(
        gridcolor="#E8EEF5",
        zerolinecolor="#D9E2EF"
    )

    fig.update_yaxes(
        gridcolor="#E8EEF5",
        zerolinecolor="#D9E2EF"
    )

    return fig


# ==========================================
# 10. MONTHLY SALES TREND
# ==========================================

st.header("📈 Sales Performance")

left, right = st.columns(2)

with left:

    st.subheader("Monthly Sales Trend")

    monthly = (
        data.groupby("month", as_index=False)["total_sales"]
        .sum()
    )

    if not monthly.empty:

        monthly["sort_date"] = pd.to_datetime(
            monthly["month"], format="%b %Y"
        )

        monthly = monthly.sort_values("sort_date")

        fig1 = px.bar(
            monthly,
            x="month",
            y="total_sales",
            text_auto=".2s",
            color_discrete_sequence=["#3685DC"],
            labels={
                "month": "Month",
                "total_sales": "Sales Revenue (₹)"
            }
        )

        fig1.update_traces(
            textposition="outside"
        )

        fig1 = make_chart(fig1)

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:
        st.info("No monthly sales data.")


# ==========================================
# 11. CITY-WISE REVENUE
# ==========================================

with right:

    st.subheader("Revenue by City")

    city_sales = (
        data.groupby("city", as_index=False)["total_sales"]
        .sum()
        .sort_values("total_sales", ascending=True)
    )

    if not city_sales.empty:

        fig2 = px.bar(
            city_sales,
            x="total_sales",
            y="city",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=["#16A085"],
            labels={
                "city": "City",
                "total_sales": "Revenue (₹)"
            }
        )

        fig2 = make_chart(fig2)

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:
        st.info("No city sales data.")


st.divider()


# ==========================================
# 12. PRODUCT AND CATEGORY ANALYSIS
# ==========================================

st.header("🛒 Product & Category Analysis")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Product-wise Revenue")

    product_sales = (
        data.groupby("product", as_index=False)["total_sales"]
        .sum()
    )

    if not product_sales.empty:

        fig3 = px.pie(
            product_sales,
            names="product",
            values="total_sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        fig3 = make_chart(fig3, 370)

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

with col2:

    st.subheader("Category-wise Revenue")

    category_sales = (
        data.groupby("category", as_index=False)["total_sales"]
        .sum()
    )

    if not category_sales.empty:

        fig4 = px.pie(
            category_sales,
            names="category",
            values="total_sales",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig4 = make_chart(fig4, 370)

        st.plotly_chart(
            fig4,
            use_container_width=True
        )


# ==========================================
# 13. PRODUCT QUANTITY ANALYSIS
# ==========================================

st.divider()

st.header("📦 Product Quantity Analysis")

quantity_sales = (
    data.groupby("product", as_index=False)["quantity"]
    .sum()
    .sort_values("quantity", ascending=True)
)

if not quantity_sales.empty:

    fig5 = px.bar(
        quantity_sales,
        x="quantity",
        y="product",
        orientation="h",
        text_auto=True,
        color_discrete_sequence=["#7955D9"],
        labels={
            "product": "Product",
            "quantity": "Quantity Sold"
        }
    )

    fig5 = make_chart(fig5, 380)

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ==========================================
# 14. DETAILED SALES TABLE
# ==========================================

st.divider()

st.header("📋 Detailed Sales Records")

st.write(f"Total records: {len(data)}")

st.dataframe(
    data,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 15. DOWNLOAD REPORT
# ==========================================

st.header("📥 Download Sales Report")

st.download_button(
    label="Download E-Commerce Report",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="ecommerce_sales_report.csv",
    mime="text/csv"
)


# ==========================================
# 16. FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    <b>E-Commerce Analytics Dashboard</b><br>
    Developed using Python | Pandas | Streamlit | Plotly
</div>
""", unsafe_allow_html=True)

import sqlite3
from pathlib import Path

# SQLite database location
LIVE_DB = Path(__file__).resolve().parent / "ecommerce.db"

st.markdown("---")
st.header("Live E-Commerce Data Monitoring")

if st.button("Refresh Live Data"):
    try:
        from live_data import collect_live_data

        new_count, all_records = collect_live_data()

        st.success(f"New records collected: {new_count}")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Live data collection failed: {e}")

if LIVE_DB.exists():
    try:
        with sqlite3.connect(LIVE_DB) as conn:
            live_df = pd.read_sql_query(
                "SELECT * FROM ecommerce_orders",
                conn
            )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Database Records", len(live_df))

        with col2:
            st.metric(
                "New API Records",
                len(live_df[
                    live_df["order_id"].astype(str).str.startswith("API-")
                ])
            )

        st.subheader("Recently Collected Orders")
        st.dataframe(
            live_df.tail(20),
            use_container_width=True
        )

        st.download_button(
            "Download Live Dataset",
            live_df.to_csv(index=False),
            file_name="live_ecommerce_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Unable to read SQLite database: {e}")
else:
    st.info("Run live_data.py first to create your SQLite database.")
