import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

# -----------------------------------------------------------
# 1. GUJARATI PRINT HTML GENERATOR
# -----------------------------------------------------------
def create_print_html(row_json):
    # This HTML is used by the JavaScript to populate the print window
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap" rel="stylesheet">
    <style>
        @page {{ size: A4; margin: 10mm; }}
        body {{ font-family: 'Noto Sans Gujarati', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #000; }}
        .title {{ text-align: center; font-size: 18px; text-decoration: underline; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        td {{ border: 1px solid #000; padding: 10px; vertical-align: top; }}
        .label {{ font-weight: bold; background-color: #f9f9f9; width: 30%; }}
        .sketch {{ height: 350px; border: 1px solid #000; margin-top: 10px; position: relative; }}
        .sr-box {{ font-size: 20px; font-weight: bold; color: #d32f2f; border: 2px solid #d32f2f; padding: 5px; }}
    </style>
</head>
<body>
    <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
    <div class="title">સર્વે ફોર્મ (Survey Form) - વિરપુર સબ ડિવિઝન</div>
    
    <table>
        <tr>
            <td class="label">અરજદારનું નામ</td>
            <td colspan="2">{row_json.get('Name Of Applicant', '')}</td>
        </tr>
        <tr>
            <td class="label">સરનામું</td>
            <td colspan="2">
                {row_json.get('Address1', '')}, {row_json.get('Address2', '')}, 
                {row_json.get('Village Or City', '')}, {row_json.get('Taluka', '')}
            </td>
        </tr>
        <tr>
            <td class="label">SR Number</td>
            <td class="sr-box">{row_json.get('SR Number', '')}</td>
            <td>મોબાઈલ: {row_json.get('Mobile Number', '')}</td>
        </tr>
        <tr>
            <td class="label">વપરાશ વિગત</td>
            <td colspan="2">
                કેટેગરી: {row_json.get('Consumer Category', '')} | 
                લોડ: {row_json.get('Demand Load', '')} {row_json.get('Load Uom', '')}
            </td>
        </tr>
    </table>

    <div style="margin-top:20px;"><b>નકશો (Sketch):</b></div>
    <div class="sketch"></div>

    <script>
        document.fonts.ready.then(function() {{
            window.print();
            // Optional: window.close();
        }});
    </script>
</body>
</html>
"""
    return base64.b64encode(html_template.encode('utf-8')).decode('utf-8')

# -----------------------------------------------------------
# 2. APP UI & FILTERS
# -----------------------------------------------------------
st.title("⚡ Subdivision SR Monitoring Dashboard")

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Load and Clean
    df = pd.read_csv(file) if file.name.endswith('csv') else pd.read_excel(file)
    df.columns = df.columns.str.strip()
    
    # Clean "NULL" and strings
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None'], "")

    # Sidebar Filters (Restored)
    st.sidebar.header("Global Filters")
    all_schemes = sorted(df["Name Of Scheme"].unique())
    sel_schemes = st.sidebar.multiselect("Select Scheme", all_schemes, default=all_schemes)
    
    all_types = sorted(df["SR Type"].unique())
    sel_types = st.sidebar.multiselect("Select SR Type", all_types, default=all_types)

    # Apply Filters
    df = df[df["Name Of Scheme"].isin(sel_schemes) & df["SR Type"].isin(sel_types)]

    # -----------------------------------------------------------
    # 3. AG-GRID WITH PRINT ICON COLUMN
    # -----------------------------------------------------------
    
    # JavaScript logic for the Print Icon
    # It creates a clickable '🖨️' icon that opens a new window with the HTML
    cells_renderer = JsCode("""
    class PrintCellRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = '<button style="cursor:pointer; background-color:#ffa500; border:none; border-radius:4px; padding:2px 8px;">🖨️ Print</button>';
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                let rowData = params.data;
                // We fetch the B64 string from a hidden logic or reconstruct it
                // To keep it simple, we use a custom event or a window function
                window.printRow(rowData);
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    def display_tab_grid(data, key):
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        # Add the Print Column at the start
        gb.configure_column(
            "Print", 
            headerName="Action", 
            cellRenderer=cells_renderer, 
            width=100, 
            pinned='left'
        )
        
        grid_options = gb.build()
        
        # Inject JavaScript into the browser to handle the window.printRow call
        # We need to generate the HTML content for the specific row clicked
        st.components.v1.html(f"""
            <script>
            window.printRow = function(data) {{
                // Construct the HTML content locally in JS to avoid round-trips
                const htmlContent = `
                    <html>
                    <head>
                        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati&display=swap" rel="stylesheet">
                        <style>
                            body {{ font-family: 'Noto Sans Gujarati', sans-serif; padding: 20px; }}
                            table {{ width: 100%; border-collapse: collapse; }}
                            td {{ border: 1px solid black; padding: 8px; }}
                            .header {{ text-align: center; font-weight: bold; font-size: 20px; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <h3 style="text-align:center">સર્વે ફોર્મ</h3>
                        <table>
                            <tr><td>અરજદાર:</td><td>${{data['Name Of Applicant'] || ''}}</td></tr>
                            <tr><td>સરનામું:</td><td>${{data['Address1'] || ''}}, ${{data['Village Or City'] || ''}}</td></tr>
                            <tr><td>SR No:</td><td><b>${{data['SR Number'] || ''}}</b></td></tr>
                            <tr><td>કેટેગરી:</td><td>${{data['Consumer Category'] || ''}}</td></tr>
                        </table>
                        <div style="margin-top:30px; border:1px solid black; height:300px;">નકશો (Sketch)</div>
                    </body>
                    <script>
                        document.fonts.ready.then(() => {{ window.print(); }});
                    </script>
                    </html>
                `;
                var w = window.open('', '_blank');
                w.document.write(htmlContent);
                w.document.close();
            }}
            </script>
        """, height=0)

        AgGrid(
            data, 
            gridOptions=grid_options, 
            allow_unsafe_jscode=True, 
            theme="streamlit", 
            key=key,
            height=500
        )

    # Tabs
    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])
    
    df_survey = df[(df["Survey Category"] == "") & (df["SR Status"].str.upper() == "OPEN")]

    with t1:
        st.write(f"Showing {len(df_survey)} records")
        display_tab_grid(df_survey, "g1")

else:
    st.info("Please upload a file to see the dashboard.")
