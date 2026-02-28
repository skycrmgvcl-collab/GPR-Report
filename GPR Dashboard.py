import streamlit as st
import pandas as pd

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xls", "xlsx", "csv"]
)

# =========================================================
# REQUIRED COLUMNS FOR UNSURVEY TAB
# =========================================================

required_columns = [
    "Name Of Subdivision",
    "SR Number",
    "SR Type",
    "Name Of Applicant",
    "Address1",
    "Address2",
    "District",
    "Taluka",
    "Village Or City",
    "Consumer Category",
    "Sub Category",
    "Name Of Scheme",
    "Demand Load",
    "Load Uom",
    "Tariff",
    "RC Date",
    "RC MR NO",
    "RC Charge",
    "SR Status",
    "Rev Land Syrvey No"
]

# =========================================================
# READ FILE
# =========================================================

if uploaded_file is not None:

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

    # =====================================================
    # REMOVE EXCLUDED DATA
    # =====================================================

    if "SR Type" in df.columns:
        df = df[df["SR Type"].astype(str).str.strip().str.lower() != "change of name"]

    if "Name Of Scheme" in df.columns:
        df = df[df["Name Of Scheme"].astype(str).str.strip().str.lower() != "spa schemes"]

    # =====================================================
    # DATE CONVERSION
    # =====================================================

    if "RC Date" in df.columns:
        df["RC Date"] = pd.to_datetime(df["RC Date"], errors="coerce")

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs([
        "📝 Unsurvey Applications",
        "📄 FQ Pending",
        "💰 Paid Pending"
    ])

    # =====================================================
    # UNSURVEY TAB WITH OPEN STATUS
    # =====================================================

    with tab1:

        st.subheader("Unsurvey Applications (OPEN status only)")

        unsurvey_df = df[
            (
                df["Survey Category"].isna()
                | (df["Survey Category"].astype(str).str.strip() == "")
                | (df["Survey Category"].astype(str).str.lower() == "nan")
            )
            &
            (df["SR Status"].astype(str).str.upper() == "OPEN")
        ]

        # Select only required columns
        unsurvey_df = unsurvey_df[required_columns]

        st.metric("Total Unsurvey OPEN Applications", len(unsurvey_df))

        # =================================================
        # DISPLAY TABLE WITH SURVEY BUTTON
        # =================================================

        for index, row in unsurvey_df.iterrows():

            col1, col2 = st.columns([10, 1])

            with col1:
                st.write(
                    f"**SR Number:** {row['SR Number']} | "
                    f"**Applicant:** {row['Name Of Applicant']} | "
                    f"**Village:** {row['Village Or City']} | "
                    f"**Load:** {row['Demand Load']} {row['Load Uom']}"
                )

            with col2:
                if st.button("📋", key=f"survey_{index}"):

                    st.session_state["selected_sr"] = row.to_dict()

        # =================================================
        # SURVEY FORM
        # =================================================

        if "selected_sr" in st.session_state:

            st.divider()
            st.subheader("📋 Survey Form")

            sr = st.session_state["selected_sr"]

            with st.form("survey_form"):

                subdivision = st.text_input(
                    "Subdivision",
                    sr.get("Name Of Subdivision", "")
                )

                sr_number = st.text_input(
                    "SR Number",
                    sr.get("SR Number", "")
                )

                applicant = st.text_input(
                    "Applicant Name",
                    sr.get("Name Of Applicant", "")
                )

                village = st.text_input(
                    "Village",
                    sr.get("Village Or City", "")
                )

                load = st.text_input(
                    "Demand Load",
                    str(sr.get("Demand Load", ""))
                )

                survey_category = st.selectbox(
                    "Survey Category",
                    ["A", "B", "C", "D"]
                )

                remarks = st.text_area("Survey Remarks")

                submit = st.form_submit_button("Submit Survey")

                if submit:

                    st.success("Survey submitted successfully")

    # =====================================================
    # FQ PENDING TAB
    # =====================================================

    with tab2:

        fq_pending_df = df[
            (df["Survey Category"].notna())
            &
            (df["Date Of FQ Issued"].isna())
        ]

        st.metric("FQ Pending", len(fq_pending_df))

        st.dataframe(fq_pending_df)

    # =====================================================
    # PAID PENDING TAB
    # =====================================================

    with tab3:

        paid_pending_df = df[
            df["Date Of FQ Paid"].notna()
        ]

        st.metric("Paid Pending", len(paid_pending_df))

        st.dataframe(paid_pending_df)

else:

    st.info("Upload Excel or CSV file")
