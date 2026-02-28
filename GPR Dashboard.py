import streamlit as st
import pandas as pd

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xls", "xlsx", "csv"]
)

if uploaded_file is not None:

    # ================= READ FILE =================
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif uploaded_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        elif uploaded_file.name.lower().endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="xlrd")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # ================= REMOVE EXCLUDED RECORDS =================

    # Remove SR Type = Change of Name
    if "SR Type" in df.columns:
        df = df[
            df["SR Type"]
            .astype(str)
            .str.strip()
            .str.lower() != "change of name"
        ]

    # Remove Name Of Scheme = SPA Schemes
    if "Name Of Scheme" in df.columns:
        df = df[
            df["Name Of Scheme"]
            .astype(str)
            .str.strip()
            .str.lower() != "spa schemes"
        ]

    # ================= DATE CONVERSION =================

    date_cols = [
        "Date Of Survey",
        "Date Of Est Appr Launch",
        "Date Of FQ Issued",
        "Date Of FQ Paid"
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ================= CLEAN SURVEY CATEGORY =================

    if "Survey Category" in df.columns:
        df["Survey Category"] = df["Survey Category"].astype(str).str.strip()
    else:
        st.error("Survey Category column not found")
        st.stop()

    # ================= CREATE TABS =================

    tab1, tab2, tab3 = st.tabs([
        "📝 Unsurvey Applications",
        "📄 FQ Pending Applications",
        "💰 Paid Pending Applications"
    ])

    # =====================================================
    # TAB 1 — UNSURVEY
    # =====================================================

    with tab1:

        st.subheader("Unsurvey Applications")

        unsurvey_df = df[
            df["Survey Category"].isna()
            | (df["Survey Category"] == "")
            | (df["Survey Category"].str.lower() == "nan")
        ]

        st.metric("Total Unsurvey", len(unsurvey_df))

        st.dataframe(unsurvey_df, use_container_width=True)

        st.download_button(
            "Download Unsurvey List",
            unsurvey_df.to_csv(index=False),
            "unsurvey_list.csv",
            mime="text/csv"
        )

    # =====================================================
    # TAB 2 — FQ PENDING
    # =====================================================

    with tab2:

        st.subheader("FQ Pending Applications")

        fq_pending_df = df[
            (df["Survey Category"].notna())
            & (df["Survey Category"] != "")
            & (df["Survey Category"].str.lower() != "nan")
            & (df["Date Of FQ Issued"].isna())
        ]

        st.metric("Total FQ Pending", len(fq_pending_df))

        st.dataframe(fq_pending_df, use_container_width=True)

        st.download_button(
            "Download FQ Pending List",
            fq_pending_df.to_csv(index=False),
            "fq_pending_list.csv",
            mime="text/csv"
        )

    # =====================================================
    # TAB 3 — PAID PENDING (FQ PAID NOT NULL)
    # =====================================================

    with tab3:

        st.subheader("Paid Pending Applications (FQ Paid Done)")

        paid_pending_df = df[
            df["Date Of FQ Paid"].notna()
        ]

        st.metric("Total Paid Pending", len(paid_pending_df))

        st.dataframe(paid_pending_df, use_container_width=True)

        st.download_button(
            "Download Paid Pending List",
            paid_pending_df.to_csv(index=False),
            "paid_pending_list.csv",
            mime="text/csv"
        )

else:
    st.info("Please upload Excel or CSV file")
