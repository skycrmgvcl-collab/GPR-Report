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

    doc.add_paragraph("\nSite Sketch:\n")
    doc.add_paragraph("\n" * 10)

    doc.add_paragraph("\nSignature: __________________")

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

    # CLEAN
    df["SR Type"] = df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"] = df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()
    df["SR Status"] = df["SR Status"].astype(str).str.strip()

    # REMOVE EXCLUDED
    df = df[df["SR Type"].str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].str.lower() != "spa schemes"]

    if not show_connection_shift:
        df = df[df["SR Type"] != "Connection Shifting(Non Cons)"]

    if not show_pmsy:
        df = df[df["SR Type"] != "PMSY RTS"]

    # FILTER UNSURVEY OPEN
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

    # ADD SERIAL NO
    unsurvey_df.insert(0, "Sr. No.", range(1, len(unsurvey_df) + 1))

    # ADD PRINT ICON COLUMN
    unsurvey_df.insert(1, "Print", "🖨")

    st.metric("Total Unsurvey OPEN", len(unsurvey_df))

    # =====================================================
    # GRID OPTIONS
    # =====================================================

    gb = GridOptionsBuilder.from_dataframe(unsurvey_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=150
    )

    gb.configure_column("Sr. No.", maxWidth=90, flex=0)

    gb.configure_column("Print", maxWidth=90, flex=0)

    gb.configure_selection("single")

    gridOptions = gb.build()

    grid_response = AgGrid(
        unsurvey_df,
        gridOptions=gridOptions,
        height=500,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit"
    )

    selected = grid_response["selected_rows"]

    # =====================================================
    # PRINT SECTION (DIRECT PRINT FROM ICON)
    # =====================================================

    if selected is not None and len(selected) > 0:

        if isinstance(selected, pd.DataFrame):
            row = selected.iloc[0].to_dict()
        else:
            row = selected[0]

        st.divider()

        st.subheader(f"🖨 Print Survey Form – SR Number: {row['SR Number']}")

        # Proper printable layout
        print_html = f"""
        <div id="print-area">
        <h2 style='text-align:center'>Electricity Connection Survey Form</h2>
        <table border="1" style="width:100%; border-collapse:collapse;">
        """

        for col in unsurvey_columns:
            print_html += f"<tr><td><b>{col}</b></td><td>{row[col]}</td></tr>"

        print_html += """
        <tr><td><b>Survey Category</b></td><td></td></tr>
        <tr><td><b>Feeder Name</b></td><td></td></tr>
        <tr><td><b>Date of Survey</b></td><td></td></tr>
        <tr><td><b>Site Sketch</b></td><td height='200'></td></tr>
        </table>
        </div>
        """

        st.markdown(print_html, unsafe_allow_html=True)

        st.button(
            "🖨 Click here and press Ctrl+P to Print"
        )

        # Word download also available
        word_file = generate_word_form(row)

        st.download_button(
            "📄 Download Word Form",
            word_file,
            file_name=f"Survey_Form_{row['SR Number']}.docx"
        )

else:
    st.info("Upload file to begin")
