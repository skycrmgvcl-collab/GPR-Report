import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# =====================================================
# REQUIRED COLUMNS
# =====================================================

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

# =====================================================
# WORD FORM GENERATOR
# =====================================================

def generate_survey_form(data):

    doc = Document()

    # Title
    title = doc.add_heading("Electricity Connection Survey Form", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for key, value in data.items():

        row = table.add_row().cells

        row[0].text = str(key)

        row[1].text = str(value)

    doc.add_paragraph()
    doc.add_paragraph("Survey Category: _______________________")
    doc.add_paragraph("Survey Remarks: _______________________")
    doc.add_paragraph()
    doc.add_paragraph("Signature: _______________________")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xls", "xlsx", "csv"]
)

if uploaded_file is not None:

    # READ FILE

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):

        df = pd.read_excel(uploaded_file, engine="openpyxl")

    else:

        df = pd.read_excel(uploaded_file, engine="xlrd")

    # REMOVE EXCLUDED DATA

    df = df[df["SR Type"].astype(str).str.strip().str.lower() != "change of name"]

    df = df[df["Name Of Scheme"].astype(str).str.strip().str.lower() != "spa schemes"]

    # DATE FORMAT

    df["RC Date"] = pd.to_datetime(df["RC Date"], errors="coerce").dt.strftime("%d-%m-%Y")

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs(
        ["📝 Unsurvey Applications", "📄 FQ Pending", "💰 Paid Pending"]
    )

    # =====================================================
    # UNSURVEY TABLE
    # =====================================================

    with tab1:

        st.subheader("Unsurvey Applications (OPEN Only)")

        unsurvey_df = df[
            (
                df["Survey Category"].isna()
                | (df["Survey Category"].astype(str).str.strip() == "")
                | (df["Survey Category"].astype(str).str.lower() == "nan")
            )
            &
            (df["SR Status"].astype(str).str.upper() == "OPEN")
        ]

        unsurvey_df = unsurvey_df[required_columns]

        st.metric("Total Unsurvey OPEN", len(unsurvey_df))

        # SHOW TABLE WITH DOWNLOAD ICON

        for i, row in unsurvey_df.iterrows():

            cols = st.columns([10,1])

            with cols[0]:

                st.dataframe(pd.DataFrame([row]), use_container_width=True)

            with cols[1]:

                word_file = generate_survey_form(row.to_dict())

                st.download_button(
                    label="📄",
                    data=word_file,
                    file_name=f"Survey_Form_{row['SR Number']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=i
                )

    # =====================================================
    # FQ PENDING
    # =====================================================

    with tab2:

        fq_pending = df[
            (df["Survey Category"].notna())
            &
            (df["Date Of FQ Issued"].isna())
        ]

        st.dataframe(fq_pending)

    # =====================================================
    # PAID PENDING
    # =====================================================

    with tab3:

        paid_pending = df[df["Date Of FQ Paid"].notna()]

        st.dataframe(paid_pending)

else:

    st.info("Upload file to continue")
