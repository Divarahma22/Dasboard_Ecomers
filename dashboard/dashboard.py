import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Path ke direktori proyek
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
order_items_path = os.path.join(BASE_DIR, "order_items_dataset.csv")
order_payments_path = os.path.join(BASE_DIR, "order_payments_dataset.csv")

# 🔹 Fungsi untuk membaca CSV langsung dari direktori proyek
def load_csv(file_path, label):
    if os.path.exists(file_path):  # Cek apakah file ada di direktori
        return pd.read_csv(file_path)
    else:
        st.error(f"❌ File {label} tidak ditemukan di direktori proyek.")
        st.stop()

# 🔹 Load dataset tanpa unggah manual
order_items_df = load_csv(order_items_path, "Order Items Dataset")
order_payments_df = load_csv(order_payments_path, "Order Payments Dataset")

# 🔹 Cek apakah 'order_id' ada di kedua dataset
if 'order_id' not in order_items_df.columns or 'order_id' not in order_payments_df.columns:
    st.error("❌ Kolom 'order_id' tidak ditemukan di salah satu dataset.")
    st.stop()

# 🔹 Merge datasets berdasarkan 'order_id'
merged_df = order_items_df.merge(order_payments_df, on="order_id", how="inner")

# 🔹 Pastikan 'shipping_limit_date' ada & ubah ke datetime
if 'shipping_limit_date' in merged_df.columns:
    merged_df['shipping_limit_date'] = pd.to_datetime(merged_df['shipping_limit_date'], errors='coerce')
    merged_df = merged_df.dropna(subset=['shipping_limit_date'])  # Hapus data error
else:
    st.error("❌ Kolom 'shipping_limit_date' tidak ditemukan dalam dataset.")
    st.stop()

# 🔹 Sidebar untuk filter berdasarkan rentang tanggal
st.sidebar.header("🗂️ Filter Data")
min_date, max_date = merged_df['shipping_limit_date'].min(), merged_df['shipping_limit_date'].max()

start_date, end_date = st.sidebar.date_input("📆 Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)

# 🔹 Filter data berdasarkan tanggal yang dipilih
filtered_df = merged_df[(merged_df['shipping_limit_date'] >= pd.Timestamp(start_date)) & 
                         (merged_df['shipping_limit_date'] <= pd.Timestamp(end_date))]

# 🔹 Cek apakah data setelah filter kosong
if filtered_df.empty:
    st.warning("⚠️ Tidak ada data dalam rentang tanggal yang dipilih.")
    st.stop()

# 🔹 Pastikan kolom 'payment_type' & 'payment_value' ada sebelum lanjut
if 'payment_type' in filtered_df.columns and 'payment_value' in filtered_df.columns:
    st.header("💰 Total Nilai Pembayaran Berdasarkan Metode Pembayaran")
    payment_summary = filtered_df.groupby("payment_type")['payment_value'].sum().reset_index()
    st.dataframe(payment_summary)
else:
    st.warning("⚠️ Kolom 'payment_type' atau 'payment_value' tidak ditemukan.")
    payment_summary = pd.DataFrame()  # Buat dataframe kosong

# 🔹 Pastikan kolom 'payment_installments' & 'price' ada sebelum lanjut
if 'payment_installments' in filtered_df.columns and 'price' in filtered_df.columns:
    st.header("📊 Rata-rata Harga Produk Berdasarkan Jumlah Cicilan")
    installment_price = filtered_df.groupby("payment_installments")['price'].mean().reset_index()
    st.dataframe(installment_price)
else:
    st.warning("⚠️ Kolom 'payment_installments' atau 'price' tidak ditemukan.")
    installment_price = pd.DataFrame()  # Buat dataframe kosong

# 🔹 Visualisasi Total Pembayaran per Metode
if not payment_summary.empty:
    st.subheader("📈 Visualisasi Pembayaran")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='payment_type', y='payment_value', data=payment_summary, ax=ax, palette="Blues")
    ax.set_title("Total Pembayaran per Metode")
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Total Pembayaran")
    st.pyplot(fig)

# 🔹 Visualisasi Harga Rata-rata vs Cicilan
if not installment_price.empty:
    st.subheader("📉 Visualisasi Harga vs Cicilan")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='payment_installments', y='price', data=installment_price, marker='o', color='b')
    ax.set_title("Harga Rata-rata vs Cicilan")
    ax.set_xlabel("Jumlah Cicilan")
    ax.set_ylabel("Harga Rata-rata (Rp)")
    st.pyplot(fig)

st.caption("📌 Copyright © 2024")
