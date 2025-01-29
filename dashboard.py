import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import pandas as pd
import altair as alt
sns.set(style='dark')

def create_daily_bike_rent_df(df):
    # Agregasi data penyewaan berdasarkan tanggal
    daily_bike_rent_df = df.groupby(by="dteday").cnt.sum().reset_index()
    
    # Rename kolom untuk lebih deskriptif
    daily_bike_rent_df.rename(columns={
        "cnt": "Total_Bike_Rent"
    }, inplace=True)
    
    return daily_bike_rent_df

def create_hourly_bike_rent_df(df):
    #Agregasi data berdasar jam
    hourly_bike_rent_df = df.groupby(by="hr").cnt.sum().reset_index()
    hourly_bike_rent_df.rename(columns={
        "cnt":"Total_Bike_Rent"
    },inplace=True)

    return hourly_bike_rent_df

def create_rent_by_UserType_df(df):
    rent_by_UserType_df = df.groupby(by="dteday").agg({
        "casual":"sum",
        "registered":"sum"
    }).reset_index()
    
    return rent_by_UserType_df

all_df = pd.read_csv("day_hour.csv")

# Sidebar filters
with st.sidebar:
     # Menambahkan logo perusahaan
    st.image("Cobalt Blue Simple Sport Bike Logo .png")
    min_date = all_df['dteday'].min()
    max_date = all_df['dteday'].max()
    start_date, end_date = st.date_input("Select Date Range", min_value=min_date, max_value=max_date, value=[min_date, max_date])
    
    season_options = ["All Seasons", "Season 1", "Season 2", "Season 3", "Season 4"]
    selected_season = st.selectbox("Select Season", season_options)
    

    
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

# Filter dataset
filtered_df = all_df[(all_df['dteday'] >= pd.to_datetime(start_date)) &
                     (all_df['dteday'] <= pd.to_datetime(end_date))]
if selected_season != "All Seasons":
      season_mapping = {"Season 1": 1, "Season 2": 2, "Season 3": 3, "Season 4": 4}
      filtered_df = filtered_df[filtered_df['season'] == season_mapping[selected_season]]
daily_bike_rent_df = create_daily_bike_rent_df(filtered_df)
hourly_bike_rent_df = create_hourly_bike_rent_df(filtered_df)
rent_by_UserType_df = create_rent_by_UserType_df(filtered_df)

st.header("BIKE RENT DASHBOARD:sparkles:")

st.subheader("Daily Order")
col1, col2, col3 = st.columns(3)

with col1:
    total_rent_daily = daily_bike_rent_df.Total_Bike_Rent.sum()
    st.metric("Total Rent Daily:", total_rent_daily)

with col2:
    st.metric("Max Daily Rentals", daily_bike_rent_df["Total_Bike_Rent"].max())
with col3:
    st.metric("Average Hourly Rentals", round(hourly_bike_rent_df["Total_Bike_Rent"].mean(), 2))

fig, ax = plt.subplots(figsize=(16,8))
ax.plot(
    daily_bike_rent_df['dteday'],
    daily_bike_rent_df['Total_Bike_Rent'],
    marker='o',
    linewidth=2,
    color ="#90CAF9"
)
ax.tick_params(axis='y',labelsize=20)
ax.tick_params(axis='x',labelsize=15)

st.pyplot(fig)


st.subheader("Hourly Order")
col4, col5, col6 = st.columns(3)
with col4:
    total_rent_hourly = hourly_bike_rent_df.Total_Bike_Rent.sum()
    st.metric("Total Rent Hourly:", total_rent_daily)

with col5:
    st.metric("Max Hour;y Rentals", hourly_bike_rent_df["Total_Bike_Rent"].max())
with col6:
    st.metric("Average Hourly Rentals", round(hourly_bike_rent_df["Total_Bike_Rent"].mean(), 2))

fig, ax = plt.subplots(figsize=(16, 8))
ax.bar(
    hourly_bike_rent_df['hr'],
    hourly_bike_rent_df['Total_Bike_Rent'],
    color="#90CAF9",
    alpha=0.8
)
ax.set_xlabel("Hour", fontsize=15)
ax.set_ylabel("Total Bike Rent", fontsize=15)
ax.set_title("Hourly Rentals", fontsize=20)
st.pyplot(fig)


import altair as alt

st.subheader("Distribution By User Type")

# Hitung jumlah tanggal unik yang tersedia
num_dates = len(rent_by_UserType_df["dteday"].unique())

# Jika jumlah data lebih dari 40, lakukan binning (misalnya per 10 hari)
if num_dates > 40:
    bin_size = num_dates // 10  # Bagi menjadi sekitar 10 kelompok
    rent_by_UserType_df["bin"] = rent_by_UserType_df.index // bin_size
    rent_by_UserType_df_grouped = rent_by_UserType_df.groupby("bin").agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    rent_by_UserType_df_grouped["dteday"] = rent_by_UserType_df.iloc[::bin_size]["dteday"].values
else:
    rent_by_UserType_df_grouped = rent_by_UserType_df  # Gunakan data asli jika jumlahnya kecil

# Pastikan dteday bertipe string agar lebih mudah dibaca di Altair
rent_by_UserType_df_grouped["dteday"] = rent_by_UserType_df_grouped["dteday"].astype(str)

# **Perbaikan bagian transformasi**
rent_by_UserType_df_grouped = rent_by_UserType_df_grouped[["dteday", "casual", "registered"]]
rent_by_UserType_df_melted = rent_by_UserType_df_grouped.melt(
    id_vars=["dteday"], 
    var_name="User Type", 
    value_name="Total Rentals"
)


# **Gunakan Altair untuk visualisasi**
chart = alt.Chart(rent_by_UserType_df_melted).mark_bar().encode(
    x=alt.X("dteday:N", title="Date", axis=alt.Axis(labelAngle=-45)),  # Rotasi label agar tidak bertumpuk
    y=alt.Y("Total Rentals:Q", title="Total Rentals"),
    color="User Type:N",  # Gunakan warna berbeda untuk casual & registered
    tooltip=["dteday", "User Type", "Total Rentals"]  # Tooltip untuk detail saat hover
).properties(
    width=800,
    height=400,
    title="Total Rentals by User Type"
)

# Tampilkan grafik di Streamlit
st.altair_chart(chart, use_container_width=True)



st.caption('Copyright (c) Shafly 2025')

