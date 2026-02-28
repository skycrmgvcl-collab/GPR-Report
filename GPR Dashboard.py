import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# ================= REQUIRED COLUMNS =================

unsurvey_columns = [
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

# ================= WORD FORM FUNCTION =================

def generate_word_form(row):

    doc = Document()

    title = doc.add_heading("Electricity Connection Survey Form", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for col in unsurvey_columns:
        tr = table.add_row().cells
        tr[0].text = col
        tr[1].text = str(row[col])

    doc.add_paragraph("")
    doc.add_paragraph("Survey Category: __________________")
    doc.add_paragraph("Survey Remarks: __________________")
    doc.add_paragraph("")
    doc.add_paragraph("Signature: __________________")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


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

    df = df[df["SR Type"].astype(str).str.strip().str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].astype(str).str.strip().str.lower() != "spa schemes"]

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

    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()

    # ================= CREATE TABS =================

    tab1, tab2, tab3 = st.tabs([
        "📝 Unsurvey Applications",
        "📄 FQ Pending Applications",
        "💰 Paid Pending Applications"
    ])

    # =====================================================
    # TAB 1 — UNSURVEY TABLE (ONLY REQUIRED COLUMNS)
    # =====================================================

    with tab1:

        st.subheader("Unsurvey Applications")

        unsurvey_df = df[
            (
                df["Survey Category"].isna()
                | (df["Survey Category"] == "")
                | (df["Survey Category"].str.lower() == "nan")
            )
            &
            (df["SR Status"].str.upper() == "OPEN")
        ]

        unsurvey_df = unsurvey_df[unsurvey_columns]

        st.metric("Total Unsurvey", len(unsurvey_df))

        # DISPLAY TABLE
        st.dataframe(unsurvey_df, use_container_width=True)

        # SURVEY FORM ICON COLUMN BELOW TABLE
        st.write("### Survey Form")

        cols = st.columns(len(unsurvey_df))

        for i, row in unsurvey_df.iterrows():

            word_file = generate_word_form(row)

            st.download_button(
                label=f"📄 SR {row['SR Number']}",
                data=word_file,
                file_name=f"Survey_Form_{row['SR Number']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # =====================================================
    # TAB 2 — FQ PENDING
    # =====================================================

    with tab2:

        fq_pending_df = df[
            (df["Survey Category"].notna())
            & (df["Survey Category"] != "")
            & (df["Survey Category"].str.lower() != "nan")
            & (df["Date Of FQ Issued"].isna())
        ]

        st.metric("Total FQ Pending", len(fq_pending_df))

        st.dataframe(fq_pending_df, use_container_width=True)

    # =====================================================
    # TAB 3 — PAID PENDING
    # =====================================================

    with tab3:

        paid_pending_df = df[
            df["Date Of FQ Paid"].notna()
        ]

        st.metric("Total Paid Pending", len(paid_pending_df))

        st.dataframe(paid_pending_df, use_container_width=True)

else:

    st.info("Please upload Excel or CSV file")
