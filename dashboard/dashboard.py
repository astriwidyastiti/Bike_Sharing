import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    df['date'] = pd.to_datetime(df['date'])
    orders_df = df.resample('M', on='date').sum()
    return orders_df

def create_sum_casual_users_df(df):
    sum_casual_users_df = df.groupby("weekday").casual_users.sum().sort_values(ascending=False).reset_index()
    return sum_casual_users_df

def create_sum_registered_users_df(df):
    sum_registered_users_df = df.groupby("weekday").registered_users.sum().sort_values(ascending=False).reset_index()
    return sum_registered_users_df

def create_by_weather_df(df):
    by_weather_df=df.groupby('weathersit').total_users.sum().sort_values(ascending=False).reset_index()
    return by_weather_df

def create_by_season_df(df):
    byseason_df = df.groupby("season").total_users.sum().sort_values(ascending=False).reset_index()
    return byseason_df


def create_rfm_df(df):
    rfm_df = day_df.groupby(by="weekday", as_index=False).agg({
        "date": "max",
        "instant": "nunique",
        "total_users": "sum"
    })
    rfm_df.columns = ["day", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = day_df["date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df
# Prepare dataframe
day_df = pd.read_csv("dashboard\day_df.csv")

datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    

#membuat filter
min_date = day_df["date"].min()
max_date = day_df["date"].max()
 
with st.sidebar:
    # Menambahkan logo 
    st.image('dashboard/images.png')
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_casual_users_df = create_sum_casual_users_df(main_df)
sum_registered_users_df = create_sum_registered_users_df(main_df)
by_weather_df = create_by_weather_df(main_df)
by_season_df = create_by_season_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Bike Sharing Dashboard :bike:')

st.subheader('Daily Users')
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = daily_orders_df.casual_users.sum()
    st.metric("Total Casual User", value=f'{total_casual:,}')

with col2:
    total_registered = daily_orders_df.registered_users.sum()
    st.metric("Total Registered User", value=f'{total_registered:,}')

with col3:
    total_users = daily_orders_df.total_users.sum()
    st.metric("Total Users", value=f'{total_users:,}')
    
plt.figure(figsize=(10, 6))
plt.plot(daily_orders_df.index, daily_orders_df['total_users'], color='#A5C0DD')
plt.xlabel(None)
plt.ylabel(None)
plt.title('Number of Users')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
st.pyplot(plt)


st.subheader("Number of Casual Users and Registered Users")
categories=['Casual Users','Registered Users']
sum_casual=day_df['casual_users'].sum()
sum_registered=day_df['registered_users'].sum()
totals = [sum_casual, sum_registered]


colors = sns.color_palette('bright')[0:5]
plt.pie(totals, labels=categories, colors=colors, autopct='%.0f%%')
plt.title("Number of Customer based on categories", loc="center", fontsize=15)
st.pyplot(plt)


# The Effect of Weather and Season on Bike Sharing Productivity
import matplotlib.patches as mpatches
st.subheader("Number of Users by Season")
plt.figure(figsize=(15,6))
sns.barplot(x="season", y="total_users", data=day_df, palette="muted")
plt.ylabel(None)
plt.xlabel(None)
plt.title("Comparison of Number of Casual Users and Registered Users by Season")
casual_patch = mpatches.Patch(color=sns.color_palette("muted")[0], label='Casual User')
registered_patch = mpatches.Patch(color=sns.color_palette("muted")[1], label='Registered User')
plt.legend(handles=[casual_patch, registered_patch], title="User Type")
st.pyplot(plt)

import matplotlib.patches as mpatches
st.subheader("Number of Users by Weather")
plt.figure(figsize=(15,6))
sns.barplot(x="weathersit", y="total_users", data=day_df, palette="muted")
plt.ylabel(None)
plt.xlabel(None)
plt.title("Comparison of Number of Casual Users and Registered Users by Weathersit")
casual_patch = mpatches.Patch(color=sns.color_palette("muted")[0], label='Casual User')
registered_patch = mpatches.Patch(color=sns.color_palette("muted")[1], label='Registered User')
plt.legend(handles=[casual_patch, registered_patch], title="User Type")
plt.show()

# RFM Analysis
st.subheader("Best Customer Based on RFM Parameters (day)")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="day", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, hue="day", legend=False, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis ='x', labelsize=30, rotation=45)

sns.barplot(y="frequency", x="day", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, hue="day", legend=False, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=30, rotation=45)

sns.barplot(y="monetary", x="day", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, hue="day", legend=False, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=25)
ax[2].tick_params(axis='x', labelsize=30, rotation=45)

st.pyplot(fig)






st.caption(f"Copyright © 2023 All Rights Reserved Astri Widyastiti (https://www.linkedin.com/in/astriwidyastiti/)")
