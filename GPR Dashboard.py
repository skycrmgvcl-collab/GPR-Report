import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")

# -----------------------------------------------------------
# 1. JAVASCRIPT FOR PRINTING (Injected into browser)
# -----------------------------------------------------------
# This creates a function in your browser that builds the Gujarati PDF 
# from the row data without needing to talk back to the server.
js_print_script = """
<script>
window.printRow = function(data) {
    const htmlContent = `
        <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Noto Sans Gujarati', sans-serif; padding: 30px; line-height: 1.6; }
                .header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 5px; }
                .subheader { text-align: center; font-size: 16px; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; }
                td { border: 1px solid black; padding: 12px; vertical-align: top; }
                .label { font-weight: bold; background-color: #f2f2f2; width: 30%; }
                .sr-no { font-size: 22px; font-weight: bold; color: red; }
                .sketch { border: 1px solid black; height: 350px; margin-top: 20px; position: relative; }
                .sketch-text { position: absolute; top: 40%; left: 35%; color: #ccc; font-size: 30px; transform: rotate(-30deg); }
            </style>
        </head>
        <body>
            <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
            <div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
            <h2 style="text-align:center; text-decoration: underline;">સર્વે ફોર્મ (Survey Form)</h2>
            
            <table>
                <tr>
                    <td class="label">અરજદારનું નામ</td>
                    <td colspan="2">${data['Name Of Applicant'] || ''}</td>
                </tr>
                <tr>
                    <td class="label">સરનામું</td>
                    <td colspan="2">
                        ${data['Address1'] || ''} ${data['Address2'] || ''},<br>
                        ${data['Village Or City'] || ''}, ${data['Taluka'] || ''}, ${data['District'] || ''}
                    </td>
                </tr>
                <tr>
                    <td class="label">SR Number</td>
                    <td class="sr-no">${data['SR Number'] || ''}</td>
                    <td><b>મોબાઈલ:</b> ${data['Mobile Number'] || ''}</td>
                </tr>
                <tr>
                    <td class="label">વપરાશની વિગત</td>
                    <td colspan="2">
                        હેતુ: ${data['Consumer Category'] || ''} | 
                        Type: ${data['SR Type'] || ''} | 
                        Load: ${data['Demand Load'] || ''} ${data['Load Uom'] || ''}
                    </td>
                </tr>
                <tr>
                    <td class="label">રજીસ્ટ્રેશન ચાર્જ</td>
                    <td colspan="2">MR No: ${data['RC MR NO'] || ''} | Amount: ${data['RC Charge'] || ''}</td>
                </tr>
            </table>

            <div class="sketch">
                <div class="sketch-text">નકશો (SKETCH)</div>
            </div>

            <div style="margin-top: 20px; text-align: right;">
                <p>સર્વે કરનારની સહી: __________________</p>
            </div>

            <script>
                // Wait for Gujarati font to load before opening print dialog
                document.fonts.ready.then(() => {
                    window.print();
                    // window.close(); // Optional: closes tab after print
                });
            </script>
        </body>
        </html>
    `;
    var w = window.open('', '_blank');
    w.document.write(htmlContent);
    w.document.close();
}
</script>
"""
st.components.v1.html(js_print_script, height=0)

# -----------------------------------------------------------
# 2. DATA LOADING & FILTERING
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Read Data
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df_raw = pd.read_excel(file)

    # Clean data & Handle "NULL" strings
    df_raw.columns = df_raw.columns.str.strip()
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None'], "")

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    
    unique_schemes = sorted([x for x in df_raw["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Select Scheme", unique_schemes, default=unique_schemes)
    
    unique_types = sorted([x for x in df_raw["SR Type"].unique() if x != ""])
    sel_types = st.sidebar.multiselect("Select SR Type", unique_types, default=unique_types)

    # Search Bar
    search_query = st.sidebar.text_input("Search Name or SR Number")

    # APPLY FILTERS TO DATAFRAME
    df_filtered = df_raw[
        (df_raw["Name Of Scheme"].isin(sel_schemes)) & 
        (df_raw["SR Type"].isin(sel_types))
    ]

    if search_query:
        df_filtered = df_filtered[
            df_filtered["SR Number"].str.contains(search_query, case=False) | 
            df_filtered["Name Of Applicant"].str.contains(search_query, case=False)
        ]

    # -----------------------------------------------------------
    # 3. GRID WITH ACTION COLUMN
    # -----------------------------------------------------------
    
    # This bit of JS code creates the button inside the AgGrid row
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #2e7d32; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold;">
                🖨️ PDF
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => window.printRow(params.data));
        }
        getGui() { return this.eGui; }
    }
    """)

    def show_grid(data, grid_key):
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        # ADD THE PRINT COLUMN (Action Column)
        gb.configure_column(
            "Print_Action", 
            headerName="Action", 
            cellRenderer=render_print_button, 
            width=100, 
            pinned='left'
        )
        
        # Configure Pagination
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        
        gridOptions = gb.build()
        
        AgGrid(
            data, 
            gridOptions=gridOptions, 
            height=500, 
            theme="streamlit", 
            allow_unsafe_jscode=True, 
            key=grid_key,
            reload_data=True # This ensures grid updates when sidebar filters change
        )

    # -----------------------------------------------------------
    # 4. TABS & STAGES
    # -----------------------------------------------------------
    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    # Stage 1 Filter: Survey Category is empty and Status is OPEN
    df_survey = df_filtered[
        (df_filtered["Survey Category"] == "") & 
        (df_filtered["SR Status"].str.upper() == "OPEN")
    ]

    with t1:
        st.write(f"Total Found: **{len(df_survey)}**")
        if not df_survey.empty:
            show_grid(df_survey, "grid_survey")
        else:
            st.warning("No rows match the filters in this category.")

    with t2:
        df_est = df_filtered[
            (df_filtered["Survey Category"] != "") & 
            (df_filtered["Date Of Est Appr Launch"] == "")
        ]
        show_grid(df_est, "grid_estimate")

else:
    st.info("👋 Welcome! Please upload your Excel or CSV file to begin.")
