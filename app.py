import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

url = 'https://github.com/syamsulmaarip05/PROJEKVINIX/raw/refs/heads/main/data/DATA%20PROJEK%20VINIX%20baru%20(4).csv'

df = pd.read_csv(url)

df['Program Studi'] = df['Program Studi'].str.title().str.strip()
df['Program Studi'] = df['Program Studi'].apply(lambda x: re.sub(r'\s+', ' ', x))

st.set_page_config(layout="wide")
st.title("Analisis Program International Undergraduate Program (IUP) di Perguruan Tinggi Negeri Indonesia")
st.markdown("""##### Disusun Oleh: Syamsul Maarip, Nadhilah Hazrati, Difa Muflih Hilmy, Fauzi Noorsyabani""")

# Tambahkan CSS custom
st.markdown("""
    <style>
        /* Perbesar teks label tab */
        .stTabs [data-baseweb="tab"] {
            font-size: 18px;  /* ukuran teks tab */
            padding: 10px 20px; /* ruang di sekitar teks tab */
        }
    </style>
""", unsafe_allow_html=True)

# --- Filter Universitas ---
universitas_list = df['Universitas'].unique()
selected_univ = st.selectbox("Universitas", options=universitas_list)

# --- Filter berdasarkan pilihan ---
df_univ = df[df['Universitas'] == selected_univ]

# Buat tab seperti biasa
tab1, tab2, tab3 = st.tabs(["📊 Daya Tampung", "📈 UKT", "📋 Analisis Keseluruhan"])
 
with tab1:
    # --- METRICS ---

    # Bersihkan kolom 'Daya Tampung' dan ganti 0 dengan NaN
    df_univ['Daya Tampung'] = df_univ['Daya Tampung'].replace(0, np.nan)

    total_prodi = df_univ['Program Studi'].nunique()
    total_daya = df_univ['Daya Tampung'].sum()
    rata_daya = df_univ['Daya Tampung'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Prodi", total_prodi)
    col2.metric("Total Daya Tampung", f"{total_daya:,}")
    col3.metric("Rata-Rata Daya Tampung", f"{rata_daya:.0f}")

    # --- TABEL PROGRAM STUDI ---
    st.markdown("#### 📋 Daftar Program Studi dan Daya Tampung")
    st.dataframe(df_univ[['Program Studi', 'Daya Tampung']].reset_index(drop=True), use_container_width=True)

    # --- CHART VISUALIZATION ---
    top3 = df_univ.nlargest(3, 'Daya Tampung')
    bottom3 = df_univ.nsmallest(3, 'Daya Tampung')

    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### 📉 3 Prodi Daya Tampung Paling Sedikit")
        chart_bottom = alt.Chart(bottom3).mark_bar(color='purple').encode(
            x=alt.X('Program Studi', sort='-y'),
            y=alt.Y('Daya Tampung', scale=alt.Scale(domain=[0, 100])),
            tooltip=['Program Studi', 'Daya Tampung']
        ).properties(width=300, height=300)
        st.altair_chart(chart_bottom, use_container_width=True)

    with colB:
        st.markdown("#### 📈 3 Prodi Daya Tampung Paling Banyak")
        chart_top = alt.Chart(top3).mark_bar(color='purple').encode(
            x=alt.X('Program Studi', sort='-y'),
            y=alt.Y('Daya Tampung', scale=alt.Scale(domain=[0, 100])),
            tooltip=['Program Studi', 'Daya Tampung']
        ).properties(width=300, height=300)
        st.altair_chart(chart_top, use_container_width=True)


    def gabung_dengan_dan(daftar):
        if len(daftar) == 0:
            return ""
        elif len(daftar) == 1:
            return daftar[0]
        elif len(daftar) == 2:
            return f"{daftar[0]} dan {daftar[1]}"
        else:
            return f"{', '.join(daftar[:-1])}, dan {daftar[-1]}"

    # Siapkan data untuk top dan bottom
    top3 = df_univ.nlargest(3, 'Daya Tampung')
    bottom3 = df_univ.nsmallest(3, 'Daya Tampung')

    top3_values = top3['Daya Tampung'].tolist()
    bottom3_values = bottom3['Daya Tampung'].tolist()

    # Cek jika semua data 0
    if df_univ['Daya Tampung'].sum() == 0:
        st.markdown("### Insight Analisis")
        st.markdown(f"""
        Untuk universitas **{selected_univ}**, tidak ada data daya tampung yang ditemukan untuk program studi IUP.
        """)
    else:
        # Cek apakah top dan bottom isinya sama
        same_top_bottom = set(top3['Program Studi']) == set(bottom3['Program Studi'])

        # Buat deskripsi
        top3_detail = [f"{row['Program Studi']} ({row['Daya Tampung']})" for _, row in top3.iterrows() if row['Daya Tampung'] > 0]
        bottom3_detail = [f"{row['Program Studi']} ({row['Daya Tampung']})" for _, row in bottom3.iterrows() if row['Daya Tampung'] > 0]

        top3_detail_str = gabung_dengan_dan(top3_detail)
        bottom3_detail_str = gabung_dengan_dan(bottom3_detail)

        # Hitung variasi dan rata-rata
        top_variasi = max(top3_values) - min(top3_values)
        bottom_variasi = max(bottom3_values) - min(bottom3_values)

        # Bangun kalimat insight
        top_insight = ""
        bottom_insight = ""

        if not any(top3_values):
            top_insight = "Tidak ditemukan data daya tampung terbesar pada program studi."
        else:
            top_insight = f"Program studi seperti **{top3_detail_str}** memiliki daya tampung terbesar"
            if top_variasi <= 5:
                rata_top = round(sum(top3_values) / len(top3_values))
                top_insight += f", dengan rata-rata sekitar **{rata_top} mahasiswa**"
            top_insight += "."

        if not any(bottom3_values):
            bottom_insight = "Tidak ditemukan data daya tampung terbatas pada program studi."
        elif not same_top_bottom:
            bottom_insight = f"Sedangkan program studi dengan daya tampung terbatas seperti **{bottom3_detail_str}**"
            if bottom_variasi <= 5:
                rata_bot = round(sum(bottom3_values) / len(bottom3_values))
                bottom_insight += f", dengan rata-rata sekitar **{rata_bot} mahasiswa**"
            bottom_insight += ", kemungkinan merupakan program yang memiliki fokus spesialisasi tinggi atau menghadapi batasan fasilitas dan tenaga pengajar."
        else:
            rata_semua = round(df_univ['Daya Tampung'].mean())
            top_insight = f"Seluruh program studi di universitas ini memiliki daya tampung yang relatif seragam, sekitar **{rata_semua} mahasiswa** per program studi."

        # Tampilkan ke Streamlit
        st.markdown("### Insight Analisis")
        st.markdown(f"""
        **{selected_univ}** menawarkan sebanyak **{total_prodi}** program studi IUP dengan total kapasitas **{total_daya} mahasiswa**.
        {top_insight}
        {bottom_insight}
        """)

    #sumber referensi
    # Ambil sumber unik per universitas
    sumber_unik = df_univ.groupby('Universitas')['SUMBER'].first().reset_index()
    st.markdown("### Sumber Data")
    for _, row in sumber_unik.iterrows():
        st.markdown(f"- **{row['Universitas']}**: {row['SUMBER']}")




with tab2:
    # --- Bersihkan kolom 'UKT WNI' dan ganti NaN dengan 0
    df_univ['UKT WNI'] = pd.to_numeric(df_univ['UKT WNI'], errors='coerce').fillna(0)


    # Filter data hanya yang UKT > 0 untuk analisis
    df_univ_ukt = df_univ[df_univ['UKT WNI'] > 0]

    if df_univ_ukt.empty:    
        # --- METRICS ---
        total_prodi = df_univ['Program Studi'].nunique()
        total_ukt = df_univ['UKT WNI'].sum()
        rata_ukt = df_univ['UKT WNI'].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Prodi", total_prodi)
        col2.metric("Total UKT WNI", f"{total_ukt:,.0f}")
        col3.metric("Rata-Rata UKT WNI", f"{rata_ukt:,.0f}")

        # --- TABEL PROGRAM STUDI ---
        st.markdown("#### 📋 Daftar Program Studi dan UKT WNI")
        st.dataframe(
            df_univ[['Program Studi', 'UKT WNI']].reset_index(drop=True),
            use_container_width=True
        )

        # --- CHART VISUALIZATION ---
        top3 = df_univ.nlargest(3, 'UKT WNI')
        bottom3 = df_univ.nsmallest(3, 'UKT WNI')

        colA, colB = st.columns(2)

        # Hitung nilai maksimum UKT untuk domain Y
        max_ukt = df_univ['UKT WNI'].max()
        y_domain = [0, max_ukt * 1.1]  # tambahkan 10% margin atas

        with colA:
            st.markdown("#### 📉 3 Prodi dengan UKT WNI Paling Rendah")
            chart_bottom = alt.Chart(bottom3).mark_bar(color='green').encode(
                x=alt.X('Program Studi:N', sort='-y'),
                y=alt.Y('UKT WNI:Q', scale=alt.Scale(domain=y_domain)),
                tooltip=['Program Studi', 'UKT WNI']
            ).properties(width=300, height=300)
            st.altair_chart(chart_bottom, use_container_width=True)

        with colB:
            st.markdown("#### 📈 3 Prodi dengan UKT WNI Paling Tinggi")
            chart_top = alt.Chart(top3).mark_bar(color='crimson').encode(
                x=alt.X('Program Studi:N', sort='-y'),
                y=alt.Y('UKT WNI:Q', scale=alt.Scale(domain=y_domain)),
                tooltip=['Program Studi', 'UKT WNI']
            ).properties(width=300, height=300)
            st.altair_chart(chart_top, use_container_width=True)

        #Insight Analisis
        st.markdown("### 💡 Insight Analisis")

        st.markdown(f"""
                Data UKT **Belum Ditemukan** untuk **{selected_univ}**.
        """)
        

    else:
        # Ganti nilai 0 dengan NaN
        df_univ['UKT WNI'] = df_univ['UKT WNI'].replace(0, np.nan)

        # --- METRICS ---
        total_prodi = df_univ['Program Studi'].nunique()
        total_ukt = df_univ['UKT WNI'].sum()
        rata_ukt = df_univ['UKT WNI'].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Prodi", total_prodi)
        col2.metric("Total UKT WNI", f"{total_ukt:,.0f}")
        col3.metric("Rata-Rata UKT WNI", f"{rata_ukt:,.2f}")

        # --- TABEL PROGRAM STUDI ---
        st.markdown("#### 📋 Daftar Program Studi dan UKT WNI")
        st.dataframe(
            df_univ[['Program Studi', 'UKT WNI']].reset_index(drop=True),
            use_container_width=True
        )

        # --- CHART VISUALIZATION ---
        top3 = df_univ.nlargest(3, 'UKT WNI')
        bottom3 = df_univ.nsmallest(3, 'UKT WNI')

        colA, colB = st.columns(2)

        max_ukt = df_univ['UKT WNI'].max()
        y_domain = [0, max_ukt * 1.1]

        with colA:
            st.markdown("#### 📉 3 Prodi dengan UKT WNI Paling Rendah")
            chart_bottom = alt.Chart(bottom3).mark_bar(color='green').encode(
                x=alt.X('Program Studi:N', sort='-y'),
                y=alt.Y('UKT WNI:Q', scale=alt.Scale(domain=y_domain)),
                tooltip=['Program Studi', 'UKT WNI']
            ).properties(width=300, height=300)
            st.altair_chart(chart_bottom, use_container_width=True)

        with colB:
            st.markdown("#### 📈 3 Prodi dengan UKT WNI Paling Tinggi")
            chart_top = alt.Chart(top3).mark_bar(color='crimson').encode(
                x=alt.X('Program Studi:N', sort='-y'),
                y=alt.Y('UKT WNI:Q', scale=alt.Scale(domain=y_domain)),
                tooltip=['Program Studi', 'UKT WNI']
            ).properties(width=300, height=300)
            st.altair_chart(chart_top, use_container_width=True)

        # --- Helper Function ---
        def gabung_dengan_dan(daftar):
            if len(daftar) == 0:
                return ""
            elif len(daftar) == 1:
                return daftar[0]
            elif len(daftar) == 2:
                return f"{daftar[0]} dan {daftar[1]}"
            else:
                return f"{', '.join(daftar[:-1])}, dan {daftar[-1]}"

        # --- Detail untuk Insight ---
        top3_detail = [f"{row['Program Studi']} (Rp {row['UKT WNI']:,.0f})" for _, row in top3.iterrows() if not pd.isna(row['UKT WNI'])]
        bottom3_detail = [f"{row['Program Studi']} (Rp {row['UKT WNI']:,.0f})" for _, row in bottom3.iterrows() if not pd.isna(row['UKT WNI'])]

        top3_str = gabung_dengan_dan(top3_detail)
        bottom3_str = gabung_dengan_dan(bottom3_detail)

        ukt0_list = df_univ[df_univ['UKT WNI'].isna()]['Program Studi'].tolist()
        ukt0_str = gabung_dengan_dan(ukt0_list)
        ukt0 = len(ukt0_list) > 0

        # --- Ambil nilai tertinggi, terendah, dan selisih ---
        ukt_tertinggi = df_univ['UKT WNI'].max()
        ukt_terendah = df_univ['UKT WNI'].min()
        selisih = ukt_tertinggi - ukt_terendah if pd.notna(ukt_tertinggi) and pd.notna(ukt_terendah) else None

        # --- Insight ---
        st.markdown("### 💡 Insight Analisis")

        if ukt_tertinggi == ukt_terendah:
            if ukt0:
                st.markdown(f"""
                    Semua program studi IUP di **{selected_univ}** memiliki UKT WNI yang seragam sebesar **Rp {ukt_tertinggi:,.0f}**.
                    Hal ini menunjukkan kebijakan tarif yang merata tanpa perbedaan antar prodi.
                    Terdapat juga program studi tanpa data UKT, yaitu: **{ukt0_str}**
                """)
            else:
                st.markdown(f"""
                    Semua program studi IUP di **{selected_univ}** memiliki UKT WNI yang seragam sebesar **Rp {ukt_tertinggi:,.0f}**.
                    Hal ini menunjukkan kebijakan tarif yang merata tanpa perbedaan antar prodi.
                """)
        else:
            if ukt0:
                st.markdown(f"""
                    Universitas **{selected_univ}** memiliki **{total_prodi}** program studi IUP.
                    UKT WNI tertinggi adalah pada prodi **{top3_detail[0]}**, dan 3 prodi dengan UKT terendah adalah **{bottom3_str}**.
                    Selisih antara UKT WNI tertinggi dan terendah adalah **Rp {selisih:,.0f}**.
                    Terdapat juga program studi tanpa data UKT, yaitu: **{ukt0_str}**.
                """)
            else:
                st.markdown(f"""
                    Universitas **{selected_univ}** memiliki **{total_prodi}** program studi IUP.
                    UKT WNI tertinggi adalah pada prodi **{top3_detail[0]}**, dan 3 prodi dengan UKT terendah adalah **{bottom3_str}**.
                    Selisih antara UKT WNI tertinggi dan terendah adalah **Rp {selisih:,.0f}**.
                """)
    #sumber referensi
    # Ambil sumber unik per universitas
    sumber_unik = df_univ.groupby('Universitas')['SUMBER'].first().reset_index()
    st.markdown("### Sumber Data")
    for _, row in sumber_unik.iterrows():
        st.markdown(f"- **{row['Universitas']}**: {row['SUMBER']}")

with tab3:
    # Salin dan pastikan kolom numerik
    dfsemua = df.copy()
    dfsemua['UKT WNI'] = pd.to_numeric(dfsemua['UKT WNI'], errors='coerce').fillna(0)
    dfsemua['Daya Tampung'] = pd.to_numeric(dfsemua['Daya Tampung'], errors='coerce').fillna(0)

    # Statistik umum
    total_universitas = dfsemua['Universitas'].nunique()
    rata_rataUkt = dfsemua['UKT WNI'].mean()
    rata_rataDayaTampung = dfsemua['Daya Tampung'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Universitas", total_universitas)
    col2.metric("Rata-Rata UKT", f"{rata_rataUkt:,.0f}")
    col3.metric("Rata-Rata Daya Tampung", f"{rata_rataDayaTampung:,.0f}")

    # Konversi UKT ke satuan juta
    df['UKT WNI'] = pd.to_numeric(df['UKT WNI'], errors='coerce').fillna(0) / 1e6
    df['Daya Tampung'] = pd.to_numeric(df['Daya Tampung'], errors='coerce').fillna(0)

    # Agregasi
    df_grouped = df.groupby('Universitas').agg({
        'UKT WNI': 'mean',
        'Program Studi': 'count',
        'Daya Tampung': 'mean'
    }).rename(columns={
        'UKT WNI': 'Rata-rata UKT (Juta)',
        'Program Studi': 'Jumlah Program Studi',
        'Daya Tampung': 'Rata-rata Daya Tampung'
    }).reset_index()

    # Urutkan berdasarkan UKT
    df_grouped = df_grouped.sort_values('Rata-rata UKT (Juta)', ascending=False)

    # Tentukan nilai maksimum untuk sumbu Y agar semua data muat
    max_ukt = df_grouped['Rata-rata UKT (Juta)'].max()
    max_daya = df_grouped['Rata-rata Daya Tampung'].max()
    max_prodi = df_grouped['Jumlah Program Studi'].max()
    max_y = max(max_ukt, max_daya, max_prodi)
    buffer_y = max_y * 1.2  # Tambahan ruang di atas grafik

    # Buat grafik batang
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_grouped['Universitas'],
        y=df_grouped['Rata-rata UKT (Juta)'],
        name='Rata-rata UKT (Juta)',
        marker_color='purple',
        text=df_grouped['Rata-rata UKT (Juta)'].round(1).astype(str) + "M",
        textposition='outside',
        hovertemplate='UKT: %{text}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_grouped['Universitas'],
        y=df_grouped['Rata-rata Daya Tampung'],
        name='Rata-rata Daya Tampung',
        marker_color='green',
        text=df_grouped['Rata-rata Daya Tampung'].round().astype(int).astype(str),
        textposition='outside',
        hovertemplate='Daya Tampung: %{text}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_grouped['Universitas'],
        y=df_grouped['Jumlah Program Studi'],
        name='Jumlah Prodi',
        marker_color='magenta',
        text=df_grouped['Jumlah Program Studi'].astype(str),
        textposition='outside',
        hovertemplate='Jumlah Prodi: %{text}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title='PERBANDINGAN UKT (Juta), DAYA TAMPUNG & JUMLAH PRODI (Nilai Asli)',
        xaxis=dict(title='Universitas', tickangle=-45),
        yaxis=dict(
            title='Nilai Asli (UKT dalam Juta)',
            range=[0, buffer_y],
            showgrid=True
        ),
        barmode='group',
        legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'),
        height=600,
        margin=dict(t=100)
    )

    st.plotly_chart(fig, use_container_width=True)


    st.markdown("""### 💡 Insight Analisis""")
    st.markdown(f"""
        Visualisasi ini menggambarkan perbandingan rata-rata UKT, jumlah program studi, dan daya tampung dari 12 universitas di Indonesia. Institut Teknologi Bandung (ITB) dan Universitas Indonesia (UI) memiliki rata-rata UKT tertinggi, masing-masing sebesar 30 juta dan 28,6 juta rupiah. Kedua universitas ini juga dikenal memiliki banyak program studi dengan kebutuhan operasional tinggi, seperti teknik dan kesehatan. UI sendiri tercatat memiliki jumlah program studi terbanyak, yaitu 36, diikuti oleh Universitas Gadjah Mada (UGM) dengan 31 program.

        Dari segi daya tampung, Universitas Diponegoro (UNDIP) menempati posisi tertinggi dengan rata-rata daya tampung sebesar 62, disusul oleh Universitas Brawijaya (UB) dengan 59 dan Universitas Sebelas Maret (UNS) dengan 52. Beberapa universitas menunjukkan daya tampung yang besar meskipun memiliki jumlah program studi yang sedikit, seperti UNS dan Universitas Hasanuddin, yang dapat mengindikasikan adanya konsentrasi kapasitas pada program studi tertentu.
                
        Temuan ini menunjukkan bahwa jumlah program studi tidak selalu sebanding dengan daya tampung atau besarnya UKT. Universitas dengan jumlah program studi yang banyak cenderung memiliki cakupan keilmuan yang luas, tetapi kapasitas tampung dan biaya kuliah dapat bervariasi tergantung pada kebijakan internal masing-masing institusi. Oleh karena itu, pendekatan analisis tambahan seperti rasio daya tampung terhadap jumlah program studi dapat memberikan gambaran yang lebih proporsional.
    """)

    st.subheader("Filter Data Berdasarkan Provinsi")
    provinsi_list = dfsemua['Provinsi'].unique()
    selected_provinsi = st.selectbox("Pilih Provinsi", sorted(provinsi_list))
    filtered_by_provinsi = dfsemua[dfsemua['Provinsi'] == selected_provinsi]
    st.markdown(f"#### Data untuk Provinsi: {selected_provinsi}")
    st.dataframe(
        filtered_by_provinsi[['Universitas','Program Studi', 'UKT WNI', 'Daya Tampung']].reset_index(drop=True),
        use_container_width=True
    )

    st.subheader("Filter Data Berdasarkan Program Studi")

    prodi_list = dfsemua['Program Studi'].unique()
    selected_prodi = st.selectbox("Cari Program Studi", sorted(prodi_list))

    filtered_by_prodi = dfsemua[dfsemua['Program Studi'] == selected_prodi]
    st.markdown(f"#### Data untuk Program Studi: {selected_prodi}")
    st.dataframe(
        filtered_by_prodi[['Universitas','Program Studi', 'UKT WNI', 'Daya Tampung']].reset_index(drop=True),
        use_container_width=True
    )




