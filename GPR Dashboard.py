import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# =====================================================
# REQUIRED COLUMNS
# =====================================================

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

# =====================================================
# WORD FORM FUNCTION
# =====================================================

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


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xls", "xlsx", "csv"]
)

if uploaded_file:

    # READ FILE
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    else:
        df = pd.read_excel(uploaded_file, engine="xlrd")

    # REMOVE EXCLUDED DATA

    df = df[df["SR Type"].astype(str).str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].astype(str).str.lower() != "spa schemes"]

    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()

    # FILTER UNSURVEY + OPEN

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

    st.metric("Total Unsurvey OPEN", len(unsurvey_df))

    # ADD SURVEY COLUMN

    unsurvey_df["Survey Form"] = "📄"

    # =====================================================
    # DISPLAY GRID
    # =====================================================

    gb = GridOptionsBuilder.from_dataframe(unsurvey_df)

    gb.configure_selection("single")

    gridOptions = gb.build()

    grid_response = AgGrid(
        unsurvey_df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=500,
        allow_unsafe_jscode=True
    )

    selected = grid_response["selected_rows"]

    # =====================================================
    # DOWNLOAD WORD FORM WHEN ROW SELECTED
    # =====================================================

    if selected:

        selected_row = pd.Series(selected[0])

        word_file = generate_word_form(selected_row)

        st.download_button(
            label=f"📄 Download Survey Form for SR {selected_row['SR Number']}",
            data=word_file,
            file_name=f"Survey_Form_{selected_row['SR Number']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

else:

    st.info("Upload Excel file")
