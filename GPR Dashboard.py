import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import base64

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
        row[0].text = key
        row[1].text = str(value)

    doc.add_paragraph("\nSurvey Category: __________________")
    doc.add_paragraph("Feeder Name: __________________")
    doc.add_paragraph("Date of Survey: __________________")

    doc.add_paragraph("\nSite Sketch:")
    doc.add_paragraph("\n" * 4)

    doc.add_paragraph("\nSignature: __________________")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# PRINT WINDOW FUNCTION
# =====================================================

def open_print_window(row):

    half = len(unsurvey_columns)//2

    left = unsurvey_columns[:half]
    right = unsurvey_columns[half:]

    def make_rows(cols):
        html=""
        for col in cols:
            html += f"<tr><td><b>{col}</b></td><td>{row[col]}</td></tr>"
        return html

    html = f"""
    <html>
    <head>
    <title>Print Survey Form</title>
    <style>
    body {{
        font-family: Arial;
        padding:20px;
    }}
    table {{
        width:100%;
        border-collapse:collapse;
    }}
    td {{
        border:1px solid black;
        padding:5px;
        font-size:11px;
    }}
    .grid {{
        display:grid;
        grid-template-columns: 1fr 1fr;
        gap:10px;
    }}
    .sketch {{
        height:350px;
        border:1px solid black;
    }}
    </style>
    </head>

    <body onload="window.print()">

    <h3 style="text-align:center;">Electricity Connection Survey Form</h3>

    <div class="grid">

    <table>
    {make_rows(left)}
    </table>

    <table>
    {make_rows(right)}
    </table>

    </div>

    <br>

    <table>
    <tr><td><b>Survey Category</b></td><td></td></tr>
    <tr><td><b>Feeder Name</b></td><td></td></tr>
    <tr><td><b>Date of Survey</b></td><td></td></tr>
    </table>

    <br>

    <div class="sketch"></div>

    <br>
    Signature: __________________

    </body>
    </html>
    """

    b64 = base64.b64encode(html.encode()).decode()

    href = f'<a href="data:text/html;base64,{b64}" target="_blank">🖨 Print Survey Form</a>'

    return href


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload SR Excel/CSV File",
    type=["xlsx","xls","csv"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        df = pd.read_excel(uploaded_file, engine="xlrd")

    df["SR Type"]=df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"]=df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"]=df["Survey Category"].astype(str).str.strip()
    df["SR Status"]=df["SR Status"].astype(str).str.strip()

    df=df[df["SR Type"].str.lower()!="change of name"]
    df=df[df["Name Of Scheme"].str.lower()!="spa schemes"]

    if not show_connection_shift:
        df=df[df["SR Type"]!="Connection Shifting(Non Cons)"]

    if not show_pmsy:
        df=df[df["SR Type"]!="PMSY RTS"]

    unsurvey_df=df[
        (
            df["Survey Category"].isna()
            |(df["Survey Category"]=="")
            |(df["Survey Category"].str.lower()=="nan")
        )
        &(df["SR Status"].str.upper()=="OPEN")
    ]

    unsurvey_df=unsurvey_df[unsurvey_columns]

    unsurvey_df.insert(0,"Sr. No.",range(1,len(unsurvey_df)+1))
    unsurvey_df.insert(1,"Print","🖨")

    gb=GridOptionsBuilder.from_dataframe(unsurvey_df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        flex=1
    )

    gb.configure_selection("single")

    gridOptions=gb.build()

    grid_response=AgGrid(
        unsurvey_df,
        gridOptions=gridOptions,
        height=500,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

    selected=grid_response["selected_rows"]

    if selected is not None and len(selected)>0:

        if isinstance(selected,pd.DataFrame):
            row=selected.iloc[0].to_dict()
        else:
            row=selected[0]

        st.markdown(open_print_window(row), unsafe_allow_html=True)

        word_file=generate_word_form(row)

        st.download_button(
            "Download Word Form",
            word_file,
            file_name=f"Survey_Form_{row['SR Number']}.docx"
        )

else:

    st.info("Upload file to begin")
