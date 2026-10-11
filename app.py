import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

from drought_engine import (
    DEFAULT_FEEDS, build_queries, search_drought_news,
    enrich_dataframe, risk_summary
)
from database import save_run, load_history
from reports import make_excel

SOURCE_CATALOG_PATH = Path(__file__).with_name("sources_indonesia_sawah_irigasi.json")
try:
    SOURCE_CATALOG = json.loads(SOURCE_CATALOG_PATH.read_text(encoding="utf-8"))
except Exception:
    SOURCE_CATALOG = {}

CURATED_SOURCES = {}
for group_name, items in SOURCE_CATALOG.items():
    for item in items:
        if item.get("kind") != "Template RSS (ganti ID)":
            CURATED_SOURCES[f"{group_name} — {item['name']}"] = item["url"]

st.set_page_config(page_title="Drought Early Warning", page_icon="☀️", layout="wide")

st.title("☀️ Drought Early Warning & News Intelligence")
st.caption("Monitoring berita + sumber sosial publik/terindeks untuk indikasi kekeringan")

with st.sidebar:
    st.header("Parameter Monitoring")
    theme = st.text_input("Tema", "Kekeringan dan krisis air")
    keywords = st.text_area(
        "Kata kunci",
        "kekeringan\nkrisis air\nkemarau panjang\ndefisit air\nirigasi\nsawah\nembung\nwaduk\nair bersih\nEl Nino\nsumur mengering\ngagal panen",
        height=190,
    )
    region = st.text_input("Wilayah", "Jawa Tengah")
    days = st.slider("Rentang berita", 1, 30, 7)
    min_score = st.slider("Skor relevansi minimum", 0, 100, 20)
    max_results = st.slider("Maksimum hasil", 20, 500, 200, step=10)

    st.subheader("Sumber")
    selected = st.multiselect(
        "Feed publik",
        list(DEFAULT_FEEDS.keys()),
        default=list(DEFAULT_FEEDS.keys()),
    )
    st.subheader("Katalog sumber Indonesia")
    st.caption("Pilih feed tambahan dari katalog. Banyak URL daerah adalah query Google News RSS; hasil bergantung pada indeks Google News.")
    curated_selected = st.multiselect(
        "Sumber tambahan (nasional/daerah)",
        options=list(CURATED_SOURCES.keys()),
        default=[],
    )
    st.caption("Satu sumber per baris. Format: Nama Sumber | URL RSS. URL halaman Instagram biasa bukan RSS.")
    custom = st.text_area(
        "RSS / feed publik tambahan",
        placeholder="ANTARA | https://alamat-rss-yang-valid/feed\nYouTube BPBD | https://www.youtube.com/feeds/videos.xml?channel_id=ID_KANAL",
        height=120,
        help="Masukkan endpoint RSS/Atom yang valid. Untuk YouTube, gunakan channel_id. Untuk Instagram, diperlukan sumber publik yang benar-benar menyediakan feed/API yang sah.",
    )

    run = st.button("☀️ ANALISIS SEKARANG", type="primary", use_container_width=True)

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

if run:
    kws = [x.strip() for x in keywords.splitlines() if x.strip()]
    queries = build_queries(theme, kws, region)
    feeds = {k: DEFAULT_FEEDS[k] for k in selected}
    custom_feeds = [x.strip() for x in custom.splitlines() if x.strip()]
    for source_label in curated_selected:
        source_url = CURATED_SOURCES[source_label]
        custom_feeds.append(f"{source_label} | {source_url}")

    with st.spinner("Mengumpulkan dan menganalisis data..."):
        rows, errors = search_drought_news(
            queries, kws + [theme], feeds, custom_feeds,
            int(days), int(min_score), int(max_results)
        )
        df = enrich_dataframe(rows)

    st.session_state.df = df
    st.session_state.errors = errors
    if not df.empty:
        save_run(df, theme, region)

df = st.session_state.df

if not df.empty:
    summary = risk_summary(df)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Berita/Konten", len(df))
    c2.metric("Sumber", df["Sumber"].nunique())
    c3.metric("Risiko tinggi", int((df["Risiko"]=="TINGGI").sum()))
    c4.metric("Skor risiko", f"{summary['risk_score']:.1f}")
    c5.metric("Isu dominan", summary["dominant_topic"])

    if summary["risk_score"] >= 70:
        st.error("🔴 INDIKASI RISIKO KEKERINGAN TINGGI")
    elif summary["risk_score"] >= 45:
        st.warning("🟡 INDIKASI RISIKO KEKERINGAN SEDANG")
    else:
        st.success("🟢 INDIKASI RISIKO BERDASARKAN PEMBERITAAN: RENDAH")

    tabs = st.tabs(["📰 Intelligence", "📈 Tren", "📍 Lokasi", "🚨 Early Warning", "🕘 Histori"])

    with tabs[0]:
        st.subheader("Daftar intelligence")
        cols = ["Tanggal","Risiko","Skor Risiko","Skor","Subtema","Wilayah",
                "Tipe Sumber","Judul","Sumber","Ringkasan","URL"]
        st.dataframe(
            df[cols], use_container_width=True, hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("Buka")}
        )
        st.download_button(
            "⬇️ Download Excel",
            make_excel(df),
            file_name=f"drought_intelligence_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tabs[1]:
        st.subheader("Jumlah konten per hari")
        daily = df.assign(Hari=pd.to_datetime(df["Tanggal"]).dt.date).groupby("Hari").size()
        st.line_chart(daily)
        st.subheader("Rata-rata skor risiko")
        risk_daily = df.assign(Hari=pd.to_datetime(df["Tanggal"]).dt.date).groupby("Hari")["Skor Risiko"].mean()
        st.line_chart(risk_daily)

    with tabs[2]:
        st.subheader("Wilayah yang terdeteksi")
        st.bar_chart(df["Wilayah"].value_counts())
        st.dataframe(
            df[["Tanggal","Wilayah","Subtema","Risiko","Judul","URL"]],
            use_container_width=True, hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("Buka")}
        )

    with tabs[3]:
        st.subheader("Early Warning")
        high = df[df["Risiko"]=="TINGGI"].copy()
        if high.empty:
            st.success("Belum ada konten dengan prioritas risiko tinggi.")
        else:
            st.warning(f"{len(high)} konten masuk kategori risiko tinggi.")
            st.dataframe(
                high[["Tanggal","Skor Risiko","Subtema","Wilayah","Judul","Sumber","URL"]],
                use_container_width=True, hide_index=True,
                column_config={"URL": st.column_config.LinkColumn("Buka")}
            )
        st.markdown("### Indikator yang terdeteksi")
        for item, count in summary["indicators"].items():
            st.write(f"- **{item}**: {count}")

    with tabs[4]:
        hist = load_history()
        st.dataframe(hist, use_container_width=True, hide_index=True)

    if st.session_state.get("errors"):
        with st.expander("⚠️ Sumber gagal diambil"):
            for e in st.session_state.errors:
                st.write("- " + e)
else:
    st.info("Masukkan parameter lalu klik **ANALISIS SEKARANG**.")

st.divider()
st.caption("Drought Early Warning V3.1: menggunakan RSS/feed dan konten publik yang dapat diakses secara sah. URL profil Instagram biasa tidak otomatis dapat dibaca; integrasi API memerlukan akses/izin resmi. Tidak melakukan bypass login, CAPTCHA, private account, atau akses data nonpublik.")
