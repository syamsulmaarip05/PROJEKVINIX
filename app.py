import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.graph_objects as go
import re

# URL Data CSV
DATA_URL = 'https://github.com/syamsulmaarip05/PROJEKVINIX/raw/refs/heads/main/data/DATAPROJEKNLP.csv'

@st.cache_data # Menggunakan cache untuk mempercepat pemuatan data
def load_data(url):
    """Memuat data dari URL dan melakukan pembersihan awal pada kolom Program Studi."""
    df = pd.read_csv(url)
    df['Program Studi'] = df['Program Studi'].str.title().str.strip()
    df['Program Studi'] = df['Program Studi'].apply(lambda x: re.sub(r'\s+', ' ', x) if isinstance(x, str) else x)
    return df

def gabung_dengan_dan(daftar_item):
    """Menggabungkan daftar string menjadi kalimat yang dipisahkan koma dan kata 'dan'."""
    if not daftar_item:
        return ""
    if len(daftar_item) == 1:
        return daftar_item[0]
    if len(daftar_item) == 2:
        return f"{daftar_item[0]} dan {daftar_item[1]}"
    return f"{', '.join(daftar_item[:-1])}, dan {daftar_item[-1]}"

def render_tab_daya_tampung(df_selected_univ):
    """Merender konten untuk tab Daya Tampung."""
    st.header("Analisis Daya Tampung Program Studi")

    # Pra-pemrosesan kolom 'Daya Tampung': ganti 0 dengan NaN untuk perhitungan statistik yang akurat
    df_display = df_selected_univ.copy()
    df_display['Daya Tampung'] = pd.to_numeric(df_display['Daya Tampung'], errors='coerce').replace(0, np.nan)

    # Metrik Utama
    total_prodi = df_display['Program Studi'].nunique()
    total_daya_tampung = df_display['Daya Tampung'].sum()
    rata_rata_daya_tampung = df_display['Daya Tampung'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Program Studi IUP", total_prodi)
    col2.metric("Total Daya Tampung", f"{total_daya_tampung:,.0f}" if pd.notna(total_daya_tampung) else "N/A")
    col3.metric("Rata-Rata Daya Tampung per Prodi", f"{rata_rata_daya_tampung:,.0f}" if pd.notna(rata_rata_daya_tampung) else "N/A")

    st.markdown("---")
    st.markdown("#### 📋 Daftar Program Studi dan Daya Tampung")
    st.dataframe(
        df_display[['Program Studi', 'Daya Tampung']].reset_index(drop=True).fillna({'Daya Tampung': 'Data Tidak Tersedia'}),
        use_container_width=True
    )
    st.markdown("---")

    # Visualisasi Prodi dengan Daya Tampung Terendah dan Tertinggi
    # Hanya proses jika ada data daya tampung yang valid (bukan NaN semua)
    df_chart_data = df_display.dropna(subset=['Daya Tampung'])
    if not df_chart_data.empty:
        top3 = df_chart_data.nlargest(3, 'Daya Tampung')
        bottom3 = df_chart_data.nsmallest(3, 'Daya Tampung')

        colA, colB = st.columns(2)
        y_max_domain = max(100, df_chart_data['Daya Tampung'].max() * 1.1 if not df_chart_data['Daya Tampung'].empty else 100)


        with colA:
            st.markdown("#### 📉 3 Prodi Daya Tampung Paling Sedikit")
            if not bottom3.empty:
                chart_bottom = alt.Chart(bottom3).mark_bar(color='#6A0DAD').encode(
                    x=alt.X('Program Studi:N', sort=None, title="Program Studi"),
                    y=alt.Y('Daya Tampung:Q', title="Daya Tampung", scale=alt.Scale(domain=[0, y_max_domain])),
                    tooltip=['Program Studi', 'Daya Tampung']
                ).properties(height=350)
                st.altair_chart(chart_bottom, use_container_width=True)
            else:
                st.info("Tidak cukup data untuk menampilkan prodi dengan daya tampung paling sedikit.")

        with colB:
            st.markdown("#### 📈 3 Prodi Daya Tampung Paling Banyak")
            if not top3.empty:
                chart_top = alt.Chart(top3).mark_bar(color='#6A0DAD').encode(
                    x=alt.X('Program Studi:N', sort=None, title="Program Studi"),
                    y=alt.Y('Daya Tampung:Q', title="Daya Tampung", scale=alt.Scale(domain=[0, y_max_domain])),
                    tooltip=['Program Studi', 'Daya Tampung']
                ).properties(height=350)
                st.altair_chart(chart_top, use_container_width=True)
            else:
                st.info("Tidak cukup data untuk menampilkan prodi dengan daya tampung paling banyak.")
        st.markdown("---")
    else:
        st.info(f"Tidak ada data daya tampung yang valid untuk {df_selected_univ['Universitas'].iloc[0]} untuk divisualisasikan.")
        st.markdown("---")


    # Insight Analisis Daya Tampung
    st.markdown("### 💡 Insight Analisis Daya Tampung")
    if pd.isna(total_daya_tampung) or total_daya_tampung == 0:
        st.markdown(f"Untuk universitas **{df_selected_univ['Universitas'].iloc[0]}**, tidak ada data daya tampung yang ditemukan atau semua program studi memiliki daya tampung 0 untuk program IUP.")
    else:
        top3_detail = [f"{row['Program Studi']} ({row['Daya Tampung']:,.0f})" for _, row in top3.iterrows() if pd.notna(row['Daya Tampung']) and row['Daya Tampung'] > 0]
        bottom3_detail = [f"{row['Program Studi']} ({row['Daya Tampung']:,.0f})" for _, row in bottom3.iterrows() if pd.notna(row['Daya Tampung']) and row['Daya Tampung'] > 0]

        top3_str = gabung_dengan_dan(top3_detail)
        bottom3_str = gabung_dengan_dan(bottom3_detail)
        
        insight_text = f"**{df_selected_univ['Universitas'].iloc[0]}** menawarkan sebanyak **{total_prodi}** program studi IUP dengan total kapasitas tercatat **{total_daya_tampung:,.0f} mahasiswa** (berdasarkan data yang tersedia)."

        if top3_str:
            insight_text += f"\n\nProgram studi dengan daya tampung terbesar antara lain **{top3_str}**."
        
        if bottom3_str and set(top3['Program Studi']) != set(bottom3['Program Studi']): # Hanya tampilkan jika berbeda dari top3
            insight_text += f"\n\nSementara itu, program studi dengan daya tampung lebih terbatas (namun masih memiliki kuota) adalah **{bottom3_str}**. Ini bisa mengindikasikan program dengan spesialisasi tinggi atau keterbatasan sumber daya."
        elif not bottom3_str and top3_str :
             insight_text += "\n\nTidak ditemukan program studi dengan daya tampung yang signifikan lebih rendah (yang memiliki kuota)."
        elif set(top3['Program Studi']) == set(bottom3['Program Studi']) and top3_str:
             insight_text += f"\n\nSemua program studi yang tercatat memiliki daya tampung yang relatif serupa, sekitar **{rata_rata_daya_tampung:,.0f} mahasiswa** per program studi."
        
        st.markdown(insight_text)

    # Sumber Data
    st.markdown("---")
    st.markdown("#### Sumber Data")
    sumber_univ = df_selected_univ['SUMBER'].iloc[0] if not df_selected_univ.empty else "Tidak diketahui"
    st.markdown(f"- **{df_selected_univ['Universitas'].iloc[0]}**: {sumber_univ}")


def render_tab_ukt(df_selected_univ):
    """Merender konten untuk tab UKT."""
    st.header("Analisis Uang Kuliah Tunggal (UKT)")

    df_display_ukt = df_selected_univ.copy()
    df_display_ukt['UKT WNI'] = pd.to_numeric(df_display_ukt['UKT WNI'], errors='coerce').fillna(0) # Isi NaN dengan 0 untuk tampilan awal

    # Data untuk perhitungan statistik (rata-rata), 0 dianggap NaN jika ada data valid > 0
    df_calc_ukt = df_display_ukt.copy()
    if df_calc_ukt['UKT WNI'].gt(0).any():
        df_calc_ukt['UKT WNI'] = df_calc_ukt['UKT WNI'].replace(0, np.nan)
    
    # Metrik Utama
    total_prodi_ukt = df_display_ukt['Program Studi'].nunique()
    total_ukt_sum = df_display_ukt['UKT WNI'].sum() # Sum dari data yang NaN-nya sudah jadi 0
    rata_ukt_mean = df_calc_ukt['UKT WNI'].mean() # Mean dari data yang 0-nya jadi NaN (jika ada UKT > 0)
    if pd.isna(rata_ukt_mean): rata_ukt_mean = 0


    col1, col2, col3 = st.columns(3)
    col1.metric("Total Program Studi IUP", total_prodi_ukt)
    col2.metric("Total UKT WNI (akumulasi per prodi)", f"Rp {total_ukt_sum:,.0f}")
    col3.metric("Rata-Rata UKT WNI per Prodi", f"Rp {rata_ukt_mean:,.0f}")
    
    st.markdown("---")
    st.markdown("#### 📋 Daftar Program Studi dan UKT WNI")
    st.dataframe(
        df_display_ukt[['Program Studi', 'UKT WNI']].reset_index(drop=True).assign(
            **{'UKT WNI': lambda df: df['UKT WNI'].apply(lambda x: f"Rp {x:,.0f}" if x > 0 else "Data Tidak Tersedia/Gratis")}
        ),
        use_container_width=True
    )
    st.markdown("---")

    # Visualisasi Prodi dengan UKT Terendah dan Tertinggi
    # Hanya proses jika ada data UKT yang valid (>0)
    df_chart_ukt_data = df_calc_ukt.dropna(subset=['UKT WNI']) # Gunakan data yang sudah dihandle NaN-nya
    
    if not df_chart_ukt_data.empty:
        top3_ukt = df_chart_ukt_data.nlargest(3, 'UKT WNI')
        bottom3_ukt = df_chart_ukt_data.nsmallest(3, 'UKT WNI')

        colA, colB = st.columns(2)
        max_ukt_val = df_chart_ukt_data['UKT WNI'].max()
        y_domain_ukt = [0, max_ukt_val * 1.1 if max_ukt_val > 0 else 10000000] # Default jika max 0 atau tidak ada

        with colA:
            st.markdown("#### 📉 3 Prodi UKT WNI Paling Rendah (yang memiliki data)")
            if not bottom3_ukt.empty:
                chart_bottom_ukt = alt.Chart(bottom3_ukt).mark_bar(color='green').encode(
                    x=alt.X('Program Studi:N', sort=None, title="Program Studi"),
                    y=alt.Y('UKT WNI:Q', title="UKT WNI (Rp)", scale=alt.Scale(domain=y_domain_ukt), format=",.0f"),
                    tooltip=[alt.Tooltip('Program Studi:N'), alt.Tooltip('UKT WNI:Q', format=",.0f")]
                ).properties(height=350)
                st.altair_chart(chart_bottom_ukt, use_container_width=True)
            else:
                st.info("Tidak cukup data UKT valid (>0) untuk menampilkan prodi dengan UKT paling rendah.")

        with colB:
            st.markdown("#### 📈 3 Prodi UKT WNI Paling Tinggi")
            if not top3_ukt.empty:
                chart_top_ukt = alt.Chart(top3_ukt).mark_bar(color='crimson').encode(
                    x=alt.X('Program Studi:N', sort=None, title="Program Studi"),
                    y=alt.Y('UKT WNI:Q', title="UKT WNI (Rp)", scale=alt.Scale(domain=y_domain_ukt), format=",.0f"),
                    tooltip=[alt.Tooltip('Program Studi:N'), alt.Tooltip('UKT WNI:Q', format=",.0f")]
                ).properties(height=350)
                st.altair_chart(chart_top_ukt, use_container_width=True)
            else:
                st.info("Tidak cukup data UKT valid (>0) untuk menampilkan prodi dengan UKT paling tinggi.")
        st.markdown("---")
    else:
        st.info(f"Tidak ada data UKT yang valid (lebih dari 0) untuk {df_selected_univ['Universitas'].iloc[0]} untuk divisualisasikan.")
        st.markdown("---")

    # Insight Analisis UKT
    st.markdown("### 💡 Insight Analisis UKT")
    # Cek apakah ada data UKT yang lebih dari 0
    if not df_calc_ukt['UKT WNI'].gt(0).any(): # jika semua NaN atau 0 di df_calc_ukt
        st.markdown(f"Data UKT **Belum Ditemukan atau Semua Bernilai Nol** untuk program IUP di **{df_selected_univ['Universitas'].iloc[0]}**.")
    else:
        # Gunakan df_chart_ukt_data untuk insight karena ini hanya berisi UKT > 0
        ukt_tertinggi = df_chart_ukt_data['UKT WNI'].max()
        ukt_terendah = df_chart_ukt_data['UKT WNI'].min()
        
        top3_detail_ukt = [f"{row['Program Studi']} (Rp {row['UKT WNI']:,.0f})" for _, row in top3_ukt.iterrows()]
        bottom3_detail_ukt = [f"{row['Program Studi']} (Rp {row['UKT WNI']:,.0f})" for _, row in bottom3_ukt.iterrows()]

        top3_ukt_str = gabung_dengan_dan(top3_detail_ukt)
        bottom3_ukt_str = gabung_dengan_dan(bottom3_detail_ukt)

        # Prodi dengan UKT 0 atau tidak ada data (dari df_display_ukt)
        prodi_ukt_nol_list = df_display_ukt[df_display_ukt['UKT WNI'] == 0]['Program Studi'].tolist()
        ukt0_str = gabung_dengan_dan(prodi_ukt_nol_list)
        
        insight_text = f"Di **{df_selected_univ['Universitas'].iloc[0]}**, analisis UKT WNI untuk program IUP menunjukkan:"
        
        if ukt_tertinggi == ukt_terendah and ukt_tertinggi > 0: # Semua UKT > 0 sama
            insight_text += f"\n\nSemua program studi yang memiliki data UKT menunjukkan biaya yang seragam sebesar **Rp {ukt_tertinggi:,.0f}**."
        else:
            if top3_ukt_str:
                insight_text += f"\n\nProgram studi dengan UKT WNI tertinggi antara lain **{top3_ukt_str}**."
            if bottom3_ukt_str and top3_ukt_str != bottom3_ukt_str : # Hanya tampilkan jika berbeda
                insight_text += f"\n\nSementara itu, program studi dengan UKT WNI terendah (yang memiliki data valid) adalah **{bottom3_ukt_str}**."
            
            if pd.notna(ukt_tertinggi) and pd.notna(ukt_terendah) and ukt_tertinggi > ukt_terendah:
                selisih = ukt_tertinggi - ukt_terendah
                insight_text += f"\n\nSelisih antara UKT WNI tertinggi dan terendah yang tercatat adalah **Rp {selisih:,.0f}**."

        if ukt0_str:
            insight_text += f"\n\nProgram studi berikut memiliki data UKT nol atau tidak tersedia: **{ukt0_str}**."
        
        st.markdown(insight_text)

    # Sumber Data
    st.markdown("---")
    st.markdown("#### Sumber Data")
    sumber_univ = df_selected_univ['SUMBER'].iloc[0] if not df_selected_univ.empty else "Tidak diketahui"
    st.markdown(f"- **{df_selected_univ['Universitas'].iloc[0]}**: {sumber_univ}")


def render_tab_analisis_keseluruhan(df_all_data):
    """Merender konten untuk tab Analisis Keseluruhan."""
    st.header("Analisis Keseluruhan Perguruan Tinggi")

    df_analysis = df_all_data.copy()
    df_analysis['UKT WNI'] = pd.to_numeric(df_analysis['UKT WNI'], errors='coerce').fillna(0)
    df_analysis['Daya Tampung'] = pd.to_numeric(df_analysis['Daya Tampung'], errors='coerce').fillna(0)

    # Statistik Umum Keseluruhan
    total_universitas = df_analysis['Universitas'].nunique()
    # Untuk rata-rata keseluruhan, hitung dari prodi yang punya data > 0
    rata_rata_ukt_overall = df_analysis[df_analysis['UKT WNI'] > 0]['UKT WNI'].mean()
    rata_rata_daya_tampung_overall = df_analysis[df_analysis['Daya Tampung'] > 0]['Daya Tampung'].mean()


    col1, col2, col3 = st.columns(3)
    col1.metric("Total Universitas Terdata", total_universitas)
    col2.metric("Rata-Rata UKT WNI (Nasional, per prodi)", f"Rp {rata_rata_ukt_overall:,.0f}" if pd.notna(rata_rata_ukt_overall) else "N/A")
    col3.metric("Rata-Rata Daya Tampung (Nasional, per prodi)", f"{rata_rata_daya_tampung_overall:,.0f}" if pd.notna(rata_rata_daya_tampung_overall) else "N/A")
    st.markdown("---")

    # Agregasi data per universitas untuk perbandingan
    # UKT dalam juta untuk grafik
    df_analysis_grouped = df_analysis.groupby('Universitas').agg(
        rata_rata_ukt_juta=('UKT WNI', lambda x: x[x > 0].mean() / 1e6 if x[x > 0].any() else 0), # Rata-rata dari UKT > 0, lalu bagi sejuta
        jumlah_prodi=('Program Studi', 'count'),
        rata_rata_daya_tampung=('Daya Tampung', lambda x: x[x > 0].mean() if x[x > 0].any() else 0) # Rata-rata dari Daya Tampung > 0
    ).reset_index()

    df_analysis_grouped = df_analysis_grouped.sort_values('rata_rata_ukt_juta', ascending=False)
    
    # Grafik Perbandingan Antar Universitas
    st.markdown("#### 📊 Perbandingan Rata-Rata UKT, Jumlah Prodi, dan Rata-Rata Daya Tampung Antar Universitas")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_analysis_grouped['Universitas'],
        y=df_analysis_grouped['rata_rata_ukt_juta'],
        name='Rata-rata UKT (Juta Rp)',
        marker_color='#6A0DAD', # Ungu
        text=df_analysis_grouped['rata_rata_ukt_juta'].round(1).astype(str) + " Jt",
        textposition='outside',
        hovertemplate='Rata-rata UKT: %{y:.1f} Juta Rp<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=df_analysis_grouped['Universitas'],
        y=df_analysis_grouped['rata_rata_daya_tampung'],
        name='Rata-rata Daya Tampung',
        marker_color='green',
        text=df_analysis_grouped['rata_rata_daya_tampung'].round(0).astype(int).astype(str),
        textposition='outside',
        hovertemplate='Rata-rata Daya Tampung: %{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=df_analysis_grouped['Universitas'],
        y=df_analysis_grouped['jumlah_prodi'],
        name='Jumlah Program Studi',
        marker_color='orange',
        text=df_analysis_grouped['jumlah_prodi'].astype(str),
        textposition='outside',
        hovertemplate='Jumlah Prodi: %{y}<extra></extra>'
    ))

    max_y_val = max(
        df_analysis_grouped['rata_rata_ukt_juta'].max() if not df_analysis_grouped.empty else 0,
        df_analysis_grouped['rata_rata_daya_tampung'].max() if not df_analysis_grouped.empty else 0,
        df_analysis_grouped['jumlah_prodi'].max() if not df_analysis_grouped.empty else 0,
    )
    buffer_y_overall = max_y_val * 1.25 if max_y_val > 0 else 100


    fig.update_layout(
        title_text='Perbandingan UKT (Juta Rp), Daya Tampung & Jumlah Prodi IUP',
        xaxis_title='Universitas',
        yaxis_title='Nilai',
        yaxis_range=[0, buffer_y_overall],
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=600,
        margin=dict(t=100, b=50),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # Insight Analisis Keseluruhan
    st.markdown("### 💡 Insight Analisis Keseluruhan")
    if not df_analysis_grouped.empty:
        top_ukt_overall = df_analysis_grouped.nlargest(2, 'rata_rata_ukt_juta')
        top_prodi_overall = df_analysis_grouped.nlargest(2, 'jumlah_prodi')
        top_daya_overall = df_analysis_grouped.nlargest(3, 'rata_rata_daya_tampung')

        insight_overall_text = "Dari analisis keseluruhan data program IUP di berbagai PTN:"
        
        if not top_ukt_overall.empty:
            uni_ukt1_o, ukt1_o = top_ukt_overall.iloc[0]['Universitas'], top_ukt_overall.iloc[0]['rata_rata_ukt_juta']
            insight_overall_text += f"\n\n- Universitas dengan **rata-rata UKT tertinggi** adalah **{uni_ukt1_o}** ({ukt1_o:.1f} juta Rp)."
            if len(top_ukt_overall) > 1:
                uni_ukt2_o, ukt2_o = top_ukt_overall.iloc[1]['Universitas'], top_ukt_overall.iloc[1]['rata_rata_ukt_juta']
                insight_overall_text += f" Diikuti oleh **{uni_ukt2_o}** ({ukt2_o:.1f} juta Rp)."

        if not top_prodi_overall.empty:
            uni_prodi1_o, prodi1_o = top_prodi_overall.iloc[0]['Universitas'], int(top_prodi_overall.iloc[0]['jumlah_prodi'])
            insight_overall_text += f"\n\n- **{uni_prodi1_o}** memiliki **jumlah program studi IUP terbanyak** ({prodi1_o} prodi)."
            if len(top_prodi_overall) > 1:
                uni_prodi2_o, prodi2_o = top_prodi_overall.iloc[1]['Universitas'], int(top_prodi_overall.iloc[1]['jumlah_prodi'])
                insight_overall_text += f" Disusul oleh **{uni_prodi2_o}** ({prodi2_o} prodi)."
        
        if not top_daya_overall.empty:
            uni_daya1_o, daya1_o = top_daya_overall.iloc[0]['Universitas'], int(top_daya_overall.iloc[0]['rata_rata_daya_tampung'])
            insight_overall_text += f"\n\n- Untuk **rata-rata daya tampung tertinggi per prodi**, **{uni_daya1_o}** menonjol dengan rata-rata {daya1_o} mahasiswa."
            if len(top_daya_overall) > 1:
                uni_daya2_o, daya2_o = top_daya_overall.iloc[1]['Universitas'], int(top_daya_overall.iloc[1]['rata_rata_daya_tampung'])
                insight_overall_text += f" Diikuti **{uni_daya2_o}** ({daya2_o} mahasiswa)"
            if len(top_daya_overall) > 2:
                uni_daya3_o, daya3_o = top_daya_overall.iloc[2]['Universitas'], int(top_daya_overall.iloc[2]['rata_rata_daya_tampung'])
                insight_overall_text += f" dan **{uni_daya3_o}** ({daya3_o} mahasiswa)."
        
        insight_overall_text += "\n\nPerlu dicatat bahwa jumlah program studi tidak selalu berkorelasi langsung dengan daya tampung total atau besaran UKT. Beberapa universitas mungkin fokus pada kualitas dengan kuota terbatas atau memiliki spesialisasi tertentu."
        st.markdown(insight_overall_text)
    else:
        st.info("Tidak cukup data agregat untuk menampilkan insight keseluruhan.")
    
    st.markdown("---")
    # Filter Tambahan
    st.subheader("🔍 Filter Data Lanjutan")

    # Filter berdasarkan Provinsi
    provinsi_list = sorted(df_analysis['Provinsi'].dropna().unique())
    selected_provinsi = st.selectbox("Pilih Provinsi untuk melihat daftar PTN & Prodi:", options=["Semua Provinsi"] + provinsi_list)
    
    df_filtered_prov = df_analysis
    if selected_provinsi != "Semua Provinsi":
        df_filtered_prov = df_analysis[df_analysis['Provinsi'] == selected_provinsi]
    
    st.markdown(f"#### Data IUP untuk Provinsi: {selected_provinsi}")
    st.dataframe(
        df_filtered_prov[['Universitas', 'Program Studi', 'UKT WNI', 'Daya Tampung']].rename(
            columns={'UKT WNI': 'UKT WNI (Rp)'}
        ).reset_index(drop=True).assign(
             **{'UKT WNI (Rp)': lambda df: df['UKT WNI (Rp)'].apply(lambda x: f"{x:,.0f}" if x > 0 else "N/A"),
                'Daya Tampung': lambda df: df['Daya Tampung'].apply(lambda x: f"{x:,.0f}" if x > 0 else "N/A")}
        ),
        use_container_width=True
    )

    # Filter berdasarkan Program Studi
    prodi_list_all = sorted(df_analysis['Program Studi'].dropna().unique())
    selected_prodi_filter = st.selectbox("Cari Universitas berdasarkan Program Studi IUP:", options=["Semua Program Studi"] + prodi_list_all)

    df_filtered_prodi = df_analysis
    if selected_prodi_filter != "Semua Program Studi":
        df_filtered_prodi = df_analysis[df_analysis['Program Studi'] == selected_prodi_filter]

    st.markdown(f"#### Data Universitas yang menawarkan Program Studi: {selected_prodi_filter}")
    st.dataframe(
        df_filtered_prodi[['Universitas', 'Program Studi', 'UKT WNI', 'Daya Tampung']].rename(
            columns={'UKT WNI': 'UKT WNI (Rp)'}
        ).reset_index(drop=True).assign(
             **{'UKT WNI (Rp)': lambda df: df['UKT WNI (Rp)'].apply(lambda x: f"{x:,.0f}" if x > 0 else "N/A"),
                'Daya Tampung': lambda df: df['Daya Tampung'].apply(lambda x: f"{x:,.0f}" if x > 0 else "N/A")}
        ),
        use_container_width=True
    )


def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(layout="wide", page_title="Analisis IUP PTN Indonesia")
    st.title("Analisis Program International Undergraduate Program (IUP) di Perguruan Tinggi Negeri Indonesia")
    st.markdown("""##### Disusun Oleh: Syamsul Maarip, Nadhilah Hazrati, Difa Muflih Hilmy, Fauzi Noorsyabani""")
    st.markdown("---")

    # Kustomisasi CSS untuk tampilan tab
    st.markdown("""
        <style>
            .stTabs [data-baseweb="tab"] {
                font-size: 18px;
                padding: 10px 20px;
            }
            /* Mengurangi margin atas pada judul utama */
            .stApp > header {
                margin-bottom: 0px !important;
            }
            h1 {
                 margin-bottom: 0.2rem; /* Mengurangi jarak bawah judul */
            }
            /* Mengurangi jarak antar markdown */
            .main .block-container > div > div > div > div > [data-testid="stMarkdownContainer"] p {
                 margin-bottom: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    df_original = load_data(DATA_URL)

    # Filter utama berdasarkan universitas
    universitas_list = sorted(df_original['Universitas'].unique())
    selected_univ_name = st.selectbox("Pilih Universitas untuk Analisis Detail:", options=universitas_list)
    st.markdown("---")
    
    # Dataframe yang sudah difilter berdasarkan universitas pilihan
    df_selected_univ_data = df_original[df_original['Universitas'] == selected_univ_name]

    # Inisialisasi Tab
    tab1, tab2, tab3 = st.tabs(["📊 Daya Tampung Universitas", "💰 UKT Universitas", "🏛️ Analisis Keseluruhan PTN"])
    
    with tab1:
        render_tab_daya_tampung(df_selected_univ_data)
    
    with tab2:
        render_tab_ukt(df_selected_univ_data)
        
    with tab3:
        render_tab_analisis_keseluruhan(df_original)

if __name__ == "__main__":
    main()
