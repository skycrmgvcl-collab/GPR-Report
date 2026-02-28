import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("SR Type Filter")

show_connection_shift = st.sidebar.checkbox(
    "Connection Shifting (Non Cons)", value=False
)

show_pmsy = st.sidebar.checkbox(
    "PMSY RTS", value=False
)

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

def generate_word_form(data):

    doc = Document()

    title = doc.add_heading("Electricity Connection Survey Form", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for key, value in data.items():
        row = table.add_row().cells
        row[0].text = str(key)
        row[1].text = str(value)

    doc.add_paragraph("")
    doc.add_paragraph("Survey Category: __________________")
    doc.add_paragraph("Remarks: __________________")
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
    type=["xlsx", "xls", "csv"]
)

if uploaded_file:

    # READ FILE
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    else:
        df = pd.read_excel(uploaded_file, engine="xlrd")

    # CLEAN TEXT
    df["SR Type"] = df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"] = df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()
    df["SR Status"] = df["SR Status"].astype(str).str.strip()

    # REMOVE ALWAYS EXCLUDED
    df = df[df["SR Type"].str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].str.lower() != "spa schemes"]

    # SIDEBAR FILTERS
    if not show_connection_shift:
        df = df[df["SR Type"] != "Connection Shifting(Non Cons)"]

    if not show_pmsy:
        df = df[df["SR Type"] != "PMSY RTS"]

    # UNSURVEY + OPEN FILTER
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

    # ADD SURVEY BUTTON COLUMN
    unsurvey_df["Survey Form"] = "Open Survey Form"

    st.metric("Total Unsurvey OPEN", len(unsurvey_df))

    # =====================================================
    # AGGRID TABLE
    # =====================================================

    gb = GridOptionsBuilder.from_dataframe(unsurvey_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )

    gb.configure_selection("single")

    gridOptions = gb.build()

    grid_response = AgGrid(
        unsurvey_df,
        gridOptions=gridOptions,
        height=500,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

    selected = grid_response["selected_rows"]

    # =====================================================
    # EDITABLE SURVEY FORM
    # =====================================================

    if selected is not None and len(selected) > 0:

        selected_row = selected[0]

        st.divider()
        st.subheader(f"📋 Survey Form — SR Number: {selected_row['SR Number']}")

        with st.form("survey_form"):

            form_data = {}

            for col in unsurvey_columns:

                form_data[col] = st.text_input(
                    col,
                    value=str(selected_row[col])
                )

            form_data["Survey Category"] = st.selectbox(
                "Survey Category",
                ["", "A", "B", "C", "D"]
            )

            form_data["Remarks"] = st.text_area("Remarks")

            col1, col2 = st.columns(2)

            generate_btn = col1.form_submit_button("📄 Generate Word Form")
            print_btn = col2.form_submit_button("🖨 Print Form")

        if generate_btn:

            word_file = generate_word_form(form_data)

            st.download_button(
                "Download Survey Form",
                word_file,
                file_name=f"Survey_Form_{form_data['SR Number']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        if print_btn:

            st.write("### Printable Survey Form")

            for key, value in form_data.items():
                st.write(f"**{key}:** {value}")

            st.info("Press Ctrl+P to Print")

else:
    st.info("Upload file to begin")
