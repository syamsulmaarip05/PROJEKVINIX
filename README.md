# Analisis Program International Undergraduate Program (IUP) di Perguruan Tinggi Negeri Indonesia

## Overview
Aplikasi ini menyediakan analisis visual dan insight mengenai program International Undergraduate Program (IUP) di berbagai Perguruan Tinggi Negeri di Indonesia. Aplikasi menggunakan Streamlit untuk visualisasi interaktif data UKT (Uang Kuliah Tunggal) dan daya tampung program IUP.

## Fitur
Aplikasi ini memiliki beberapa fitur utama, yang diorganisir dalam tiga tab:

### 1. Analisis Daya Tampung
- Visualisasi total dan rata-rata daya tampung per universitas
- Display 3 program studi dengan daya tampung tertinggi dan terendah
- Insight analisis terkait kapasitas penerimaan

### 2. Analisis UKT (Uang Kuliah Tunggal)
- Perbandingan UKT WNI (Warga Negara Indonesia) untuk berbagai program studi
- Visualisasi program studi dengan UKT tertinggi dan terendah
- Insight tentang kebijakan biaya kuliah

### 3. Analisis Keseluruhan
- Perbandingan statistik antar universitas
- Visualisasi gabungan UKT, jumlah program studi, dan daya tampung
- Filter data berdasarkan provinsi
- Filter data berdasarkan program studi

## Penggunaan
1. Pilih universitas dari dropdown menu di bagian atas
2. Navigasi antar tab untuk melihat analisis yang berbeda:
   - 📊 Daya Tampung
   - 📈 UKT
   - 📋 Analisis Keseluruhan
3. Pada tab Analisis Keseluruhan, gunakan filter tambahan untuk melihat data berdasarkan provinsi atau program studi

## Teknologi yang Digunakan
- **Streamlit**: Framework utama untuk aplikasi web
- **Pandas**: Manipulasi dan analisis data
- **Altair**: Visualisasi data untuk grafik pada tab Daya Tampung dan UKT
- **Plotly**: Visualisasi data interaktif untuk perbandingan antar universitas
- **NumPy**: Komputasi numerik
- **regex**: Membersihkan dan memformat data

## Sumber Data
Data diambil dari berbagai sumber resmi universitas, yang tercantum di bawah setiap analisis.

## Instalasi dan Menjalankan Aplikasi
1. Clone repositori ini:
```
git clone https://github.com/syamsulmaarip05/PROJEKVINIX.git
```

2. Instal dependensi:
```
pip install streamlit pandas altair numpy plotly
```

3. Jalankan aplikasi:
```
streamlit run app.py
```

## Tim Pengembang
- Syamsul Maarip
- Nadhilah Hazrati
- Difa Muflih Hilmy
- Fauzi Noorsyabani

## Catatan
Aplikasi ini mengambil data dari file CSV yang disimpan di GitHub. Pastikan Anda memiliki koneksi internet saat menjalankan aplikasi.
