import streamlit as st
import pandas as pd

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

uploaded_file = st.file_uploader("Upload SR Excel File", type=["xlsx", "csv"])

if uploaded_file is not None:

    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Convert important date columns
    date_cols = [
        'Date Of Survey',
        'Date Of Est Appr Launch',
        'Date Of FQ Issued',
        'Date Of FQ Paid'
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Clean Survey Category
    df['Survey Category'] = df['Survey Category'].astype(str).str.strip()

    # ================= TAB CREATION =================
    tab1, tab2, tab3 = st.tabs([
        "📝 Unsurvey Applications",
        "📄 FQ Pending Applications",
        "💰 Paid Pending Applications"
    ])

    # =====================================================
    # 1️⃣ UNSURVEY APPLICATIONS
    # =====================================================
    with tab1:
        st.subheader("Unsurvey Applications (Survey Category is NULL)")

        unsurvey_df = df[
            df['Survey Category'].isna() |
            (df['Survey Category'] == '') |
            (df['Survey Category'].str.lower() == 'nan')
        ]

        st.metric("Total Unsurvey Applications", len(unsurvey_df))
        st.dataframe(unsurvey_df, use_container_width=True)

        st.download_button(
            "Download Unsurvey List",
            unsurvey_df.to_csv(index=False),
            file_name="unsurvey_applications.csv"
        )

    # =====================================================
    # 2️⃣ FQ PENDING (Survey Done but FQ Not Issued)
    # =====================================================
    with tab2:
        st.subheader("FQ Pending (Survey Category Available but FQ Not Issued)")

        fq_pending_df = df[
            (df['Survey Category'].notna()) &
            (df['Survey Category'] != '') &
            (df['Date Of FQ Issued'].isna())
        ]

        st.metric("Total FQ Pending", len(fq_pending_df))
        st.dataframe(fq_pending_df, use_container_width=True)

        st.download_button(
            "Download FQ Pending List",
            fq_pending_df.to_csv(index=False),
            file_name="fq_pending_list.csv"
        )

    # =====================================================
    # 3️⃣ PAID PENDING LIST
    # Condition:
    # Estimate Issued + Survey Category in B,C,D
    # =====================================================
    with tab3:
        st.subheader("Paid Pending (Estimate Issued & Survey Category B/C/D)")

        paid_pending_df = df[
            (df['Date Of Est Appr Launch'].notna()) &
            (df['Survey Category'].isin(['B', 'C', 'D']))
        ]

        st.metric("Total Paid Pending", len(paid_pending_df))
        st.dataframe(paid_pending_df, use_container_width=True)

        st.download_button(
            "Download Paid Pending List",
            paid_pending_df.to_csv(index=False),
            file_name="paid_pending_list.csv"
        )

else:
    st.info("Please upload SR Excel file.")
