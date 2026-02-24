# 📊 E-Commerce Data Analysis Dashboard

Proyek ini merupakan analisis data penjualan e-commerce yang bertujuan untuk mengidentifikasi pola penjualan, performa produk, serta perilaku pelanggan. Analisis dilakukan menggunakan Python dengan pendekatan Exploratory Data Analysis (EDA) dan metode RFM Analysis (Recency, Frequency, Monetary) untuk segmentasi pelanggan.

Hasil analisis divisualisasikan dalam bentuk dashboard interaktif menggunakan Streamlit, sehingga insight yang diperoleh dapat dipahami secara lebih jelas, terstruktur, dan mudah diakses.

## Features

Dashboard ini menampilkan:

- Total Orders & Total Revenue
- Best & Worst Performing Product
- Top State by Orders & Revenue
- Distribution of Review Score
- Payment Method Analysis
- RFM Analysis (Recency, Frequency, Monetary)

## Setup Environment - Anaconda

```
conda create --name final-ds python=3.9
conda activate final-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir Project_Akhir
cd Project_Akhir
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app

```
streamlit run dashboard.py
```
