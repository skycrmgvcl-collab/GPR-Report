import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# =====================================================
# SIDEBAR FILTER
# =====================================================

st.sidebar.header("Filter Options")

include_special = st.sidebar.checkbox(
    "Include Connection Shifting(Non Cons) & PMSY RTS",
    value=False
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
# WORD GENERATOR
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

    # REMOVE EXCLUDED TYPES
    df = df[df["SR Type"].astype(str).str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].astype(str).str.lower() != "spa schemes"]

    if not include_special:
        df = df[
            ~df["SR Type"].isin([
                "Connection Shifting(Non Cons)",
                "PMSY RTS"
            ])
        ]

    df["Survey Category"] = df["Survey Category"].astype(str)

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

    # =====================================================
    # AGGRID TABLE WITH HEADER FILTERS
    # =====================================================

    gb = GridOptionsBuilder.from_dataframe(unsurvey_df)

    gb.configure_default_column(
        filter=True,
        sortable=True
    )

    gb.configure_selection("single")

    gridOptions = gb.build()

    grid = AgGrid(
        unsurvey_df,
        gridOptions=gridOptions,
        height=500,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

    selected = grid["selected_rows"]

    # =====================================================
    # EDITABLE SURVEY FORM
    # =====================================================

    if selected is not None and len(selected) > 0:

        selected_row = selected[0]

        st.divider()
        st.subheader(f"📋 Survey Form – SR Number: {selected_row['SR Number']}")

        if "form_data" not in st.session_state:
            st.session_state.form_data = selected_row.copy()

        with st.form("survey_form"):

            form_data = {}

            for col in unsurvey_columns:

                form_data[col] = st.text_input(
                    col,
                    value=str(st.session_state.form_data.get(col, "")),
                    key=f"field_{col}"
                )

            form_data["Survey Category"] = st.selectbox(
                "Survey Category",
                ["", "A", "B", "C", "D"]
            )

            form_data["Remarks"] = st.text_area("Remarks")

            col1, col2 = st.columns(2)

            generate_btn = col1.form_submit_button("📄 Generate Word")
            print_btn = col2.form_submit_button("🖨 Print")

        st.session_state.form_data = form_data

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
    st.info("Upload file to begin.")
