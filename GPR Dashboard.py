import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# ============================================================
# REQUIRED COLUMNS FOR UNSURVEY TABLE
# ============================================================

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

# ============================================================
# FUNCTION TO GENERATE WORD FORM
# ============================================================

def generate_word_form(row):

    doc = Document()

    title = doc.add_heading("Electricity Connection Survey Form", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for col in required_columns:

        tr = table.add_row().cells
        tr[0].text = col
        tr[1].text = str(row[col])

    doc.add_paragraph("")
    doc.add_paragraph("Survey Category: ______________________")
    doc.add_paragraph("Survey Remarks: ______________________")
    doc.add_paragraph("")
    doc.add_paragraph("Signature: ______________________")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:

    # READ FILE

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    else:
        df = pd.read_excel(uploaded_file, engine="xlrd")

    # REMOVE EXCLUDED RECORDS

    df = df[df["SR Type"].astype(str).str.strip().str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].astype(str).str.strip().str.lower() != "spa schemes"]

    # FORMAT DATE

    df["RC Date"] = pd.to_datetime(df["RC Date"], errors="coerce")

    # CREATE TABS

    tab1, tab2, tab3 = st.tabs([
        "📝 Unsurvey Applications",
        "📄 FQ Pending",
        "💰 Paid Pending"
    ])

    # ========================================================
    # TAB 1 — UNSURVEY TABLE FORMAT
    # ========================================================

    with tab1:

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

        # SHOW TABLE
        st.dataframe(unsurvey_df, use_container_width=True)

        st.write("### Generate Survey Form")

        # ICON BUTTONS BELOW TABLE

        for index, row in unsurvey_df.iterrows():

            col1, col2 = st.columns([6,1])

            with col1:
                st.write(
                    f"SR: {row['SR Number']} | Applicant: {row['Name Of Applicant']} | Village: {row['Village Or City']}"
                )

            with col2:

                word_file = generate_word_form(row)

                st.download_button(
                    "📄",
                    word_file,
                    file_name=f"Survey_{row['SR Number']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"btn_{index}"
                )

    # ========================================================
    # TAB 2 — FQ PENDING
    # ========================================================

    with tab2:

        fq_pending = df[
            (df["Survey Category"].notna())
            &
            (df["Date Of FQ Issued"].isna())
        ]

        st.dataframe(fq_pending, use_container_width=True)

    # ========================================================
    # TAB 3 — PAID PENDING
    # ========================================================

    with tab3:

        paid_pending = df[
            df["Date Of FQ Paid"].notna()
        ]

        st.dataframe(paid_pending, use_container_width=True)

else:

    st.info("Upload Excel or CSV file")
