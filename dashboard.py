import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.title("📊 E-Commerce Sales Dashboard")


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_approved_at").agg(
        {"order_id": "nunique", "price": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "price": "revenue"}, inplace=True
    )

    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = (
        df.groupby("product_category_name_english")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index()
    )
    sum_order_items_df.rename(columns={"order_id": "total_orders"}, inplace=True)
    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = (
        df.groupby("customer_state")
        .agg(total_orders=("order_id", "nunique"), total_revenue=("price", "sum"))
        .sort_values(by="total_orders", ascending=False)
        .reset_index()
    )

    return bystate_df


def create_review_score_df(df):
    review_score_df = (
        df.groupby("product_category_name_english")["review_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    review_score_df.rename(
        columns={"review_score": "average_review_score"}, inplace=True
    )
    return review_score_df


def create_payment_type_df(df):
    payment_type_df = (
        df.groupby("payment_type")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .reset_index()
    )
    payment_type_df.rename(columns={"order_id": "total_orders"}, inplace=True)
    return payment_type_df


def create_rfm_df(df):
    # Group berdasarkan customer sebenarnya
    df = df.dropna(subset=["order_approved_at"])
    rfm_df = df.groupby("customer_unique_id", as_index=False).agg(
        max_order_timestamp=("order_approved_at", "max"),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum"),
    )

    # Pastikan tipe datetime
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])

    # hitung tanggal terakhir dalam dataset untuk menghitung recency
    recent_date = pd.to_datetime(df["order_approved_at"]).max()

    # Hitung recency (hari sejak transaksi terakhir)
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days

    # Hapus kolom timestamp
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


# loadd data full_df
full_df = pd.read_csv("full_df.csv")

datetime_columns = ["order_approved_at", "order_estimated_delivery_date"]
full_df.sort_values(by="order_approved_at", inplace=True)
full_df.reset_index(drop=True, inplace=True)

for col in datetime_columns:
    full_df[col] = pd.to_datetime(full_df[col])


# Sidebar Filter
min_date = full_df["order_approved_at"].min().date()
max_date = full_df["order_approved_at"].max().date()

with st.sidebar:
    # menambahkan logo
    st.image("logo.png", width=200)
    st.header("Filter Data")

    Start_date, end_date = st.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

final_df = full_df[
    (full_df["order_approved_at"] >= str(Start_date))
    & (full_df["order_approved_at"] <= str(end_date))
]

# Create DataFrames untuk masing-masing visualisasi
daily_orders_df = create_daily_orders_df(final_df)
sum_order_items_df = create_sum_order_items_df(final_df)
bystate_df = create_bystate_df(final_df)
review_score_df = create_review_score_df(final_df)
rfm_df = create_rfm_df(final_df)
payement_type_df = create_payment_type_df(final_df)


# visualisasi total order dan total revenue
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df["order_count"].sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_reveue = format_currency(
        daily_orders_df["revenue"].sum(), "USD", locale="en_US"
    )
    st.metric("Total Revenue", value=total_reveue)

fig, ax = plt.subplots(figsize=(20, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9",
)
ax.tick_params(axis="y", labelsize=15)
ax.tick_params(axis="x", labelsize=10)

st.pyplot(fig)

# visualisasi best & worst category
st.subheader("Best & Worst  Product Category")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

colors = ["#F0317D", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Best Performing Category

# Best Performing Category by total order
top_category = sum_order_items_df.head(5)

sns.barplot(
    x="total_orders",
    y="product_category_name_english",
    data=top_category,
    hue="product_category_name_english",
    palette="Blues_d",
    legend=False,
    ax=ax[0],
)

ax[0].set_xlabel("Total Orders", fontsize=16)
ax[0].set_ylabel("")
ax[0].set_title("Best Category by Total Orders", fontsize=16)

# Worst Performing Category by total order

bottom_category = sum_order_items_df.sort_values(
    by="total_orders", ascending=True
).head(5)

sns.barplot(
    x="total_orders",
    y="product_category_name_english",
    data=bottom_category,
    hue="product_category_name_english",
    palette="Reds_d",
    legend=False,
    ax=ax[1],
)

ax[1].set_xlabel("Total Orders", fontsize=14)
ax[1].set_ylabel("")
ax[1].invert_xaxis()
ax[1].set_title("Worst Category by Total Orders", fontsize=16)

plt.tight_layout()
st.pyplot(fig)

# Best Performing Category by total revenue
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))
top_category_revenue = (
    final_df.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .head(5)
)
sns.barplot(
    x="price",
    y="product_category_name_english",
    data=top_category_revenue,
    palette="Blues_d",
    ax=ax[0],
)
ax[0].set_xlabel("Total Revenue", fontsize=16)
ax[0].set_ylabel("")
ax[0].set_title("Best Category by Total Revenue", fontsize=16)

# Worst Performing Category by total revenue
bottom_category_revenue = (
    final_df.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=True)
    .reset_index()
    .head(5)
)
sns.barplot(
    x="price",
    y="product_category_name_english",
    data=bottom_category_revenue,
    palette="Reds_d",
    ax=ax[1],
)
ax[1].set_xlabel("Total Revenue", fontsize=16)
ax[1].set_ylabel("")
ax[1].invert_xaxis()
ax[1].set_title("Worst Category by Total Revenue", fontsize=16)
plt.tight_layout()
st.pyplot(fig)

# visualisasi total order & revenue by state
st.subheader("Top States by Total Orders and Revenue")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

# colors = ["#F0317D", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]


# Top State by total order

top_orders = bystate_df.head(5).sort_values(by="total_orders", ascending=False)

sns.barplot(
    y="total_orders",
    x="customer_state",
    data=top_orders,
    hue="customer_state",
    palette="pink",
    legend=False,
    ax=ax[0],
)

ax[0].set_xlabel("State", fontsize=16)
ax[0].set_ylabel("")
ax[0].set_title("Top State by Total Orders", fontsize=20)

# best Performing State by revenue
top_revenue = bystate_df.head(5).sort_values(by="total_revenue", ascending=False)

sns.barplot(
    y="total_revenue",
    x="customer_state",
    data=top_revenue,
    hue="customer_state",
    palette="pink",
    legend=False,
    ax=ax[1],
)

ax[1].set_xlabel("State", fontsize=16)
ax[1].set_ylabel("")
ax[1].set_title("Top State by Total Revenue", fontsize=20)
plt.tight_layout()
st.pyplot(fig)


# visualisasi average review score by category
st.subheader("Average Review Score by Product Category")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

top_review_score_df = review_score_df.head(5).sort_values(
    by="average_review_score", ascending=False
)

sns.barplot(
    x="average_review_score",
    y="product_category_name_english",
    data=top_review_score_df,
    palette="Blues_d",
    ax=ax[0],
)
ax[0].set_xlabel("Average Review Score", fontsize=16)
ax[0].set_title("Best Performing Categories by Review Score", fontsize=20)
ax[0].set_ylabel("")

# Worst Performing Category by review score
bottom_review_score_df = review_score_df.sort_values(
    by="average_review_score", ascending=True
).head(5)

sns.barplot(
    x="average_review_score",
    y="product_category_name_english",
    data=bottom_review_score_df,
    palette="Reds_d",
    ax=ax[1],
)
ax[1].set_xlabel("Average Review Score", fontsize=16)
ax[1].set_ylabel("")
ax[1].set_title("Worst Performing Categories by Review Score", fontsize=20)
plt.tight_layout()
st.pyplot(fig)

# visualisasi jumlah order berdasarkan rating
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

review_score_count_df = (
    final_df.groupby("review_score")["order_id"]
    .nunique()
    .sort_index(ascending=False)
    .reset_index()
)
review_score_count_df.rename(columns={"order_id": "total_orders"}, inplace=True)

sns.barplot(
    x="review_score",
    y="total_orders",
    data=review_score_count_df,
    palette="pink",
    ax=ax[0],
)
ax[0].set_xlabel("Review Score", fontsize=16)
ax[0].set_ylabel("Total Orders", fontsize=16)
ax[0].set_title("Total Orders by Review Score", fontsize=20)


# visualisasi total order by payment type
payement_type_df = (
    final_df.groupby("payment_type")["order_id"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index()
)
payement_type_df.rename(columns={"order_id": "total_orders"}, inplace=True)
sns.barplot(
    x="payment_type",
    y="total_orders",
    data=payement_type_df,
    palette="pink",
    ax=ax[1],
)
ax[1].set_xlabel("Payment Type", fontsize=16)
ax[1].set_ylabel("Total Orders", fontsize=16)
ax[1].set_title("Total Orders by Payment Type", fontsize=20)
plt.tight_layout()
st.pyplot(fig)

# visualisasi analisis RFM
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df["recency"].mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df["frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = f"${rfm_df['monetary'].sum():,.2f}"
    # avg_monetary = format_currency(rfm_df["monetary"].mean(),"USD", locale="es_CO")
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency",
    x="customer_unique_id",
    data=rfm_df.sort_values(by="recency", ascending=False).head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_unique_id", fontsize=16)
ax[0].set_title("By Recency (days)", loc="center", fontsize=20)
ax[0].tick_params(axis="y", labelsize=16)
ax[0].tick_params(axis="x", labelsize=3)

sns.barplot(
    y="frequency",
    x="customer_unique_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_unique_id", fontsize=16)
ax[1].set_title("By Frequency", loc="center", fontsize=20)
ax[1].tick_params(axis="y", labelsize=16)
ax[1].tick_params(axis="x", labelsize=3)

sns.barplot(
    y="monetary",
    x="customer_unique_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_unique_id", fontsize=16)
ax[2].set_title("By Monetary", loc="center", fontsize=20)
ax[2].tick_params(axis="y", labelsize=16)
ax[2].tick_params(axis="x", labelsize=3)

st.pyplot(fig)


# visualisasi top 5 high-value customers berdasarkan monetary
st.subheader("Top 5 High-Value Customers")

top_monetary = rfm_df.sort_values("monetary", ascending=False).head(5)

fig, ax = plt.subplots(figsize=(10, 3))

sns.barplot(
    x="monetary", y="customer_unique_id", data=top_monetary, palette="magma", ax=ax
)

ax.set_title("Top 5 Customers by Monetary", fontsize=16)
ax.set_xlabel("Total Spending", fontsize=16)
ax.set_ylabel("Customer ID", fontsize=16)

st.pyplot(fig, use_container_width=True)

# visualisasi top 5 high-frequency customers berdasarkan frequency

top_orders = rfm_df.sort_values("frequency", ascending=False).head(5)
fig, ax = plt.subplots(figsize=(10, 3))

sns.barplot(
    x="frequency", y="customer_unique_id", data=top_orders, palette="magma", ax=ax
)

ax.set_title("Top 5 Customers by Frequency", fontsize=16)
ax.set_xlabel("Total Orders", fontsize=16)
ax.set_ylabel("Customer ID")

st.pyplot(fig)

st.caption("Copyright (c) Sylfia Putri 2026 ")
