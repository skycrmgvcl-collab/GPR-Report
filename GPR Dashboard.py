import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.markdown("---")

# -----------------------------------------------------------
# DATA LOADING & CLEANING
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Read Data
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df_raw = pd.read_excel(file)

    # Clean data: Replace NULL/nan and fix whitespace
    df_raw.columns = df_raw.columns.str.strip()
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT'], "")

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Options")
    
    unique_schemes = sorted([x for x in df_raw["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Select Scheme", unique_schemes, default=unique_schemes)
    
    unique_types = sorted([x for x in df_raw["SR Type"].unique() if x != ""])
    sel_types = st.sidebar.multiselect("Select SR Type", unique_types, default=unique_types)

    # Search Bar
    search_query = st.sidebar.text_input("Search Name or SR Number")

    # Applying the Filters
    df_filtered = df_raw[
        (df_raw["Name Of Scheme"].isin(sel_schemes)) & 
        (df_raw["SR Type"].isin(sel_types))
    ].copy()

    if search_query:
        df_filtered = df_filtered[
            df_filtered["SR Number"].str.contains(search_query, case=False) | 
            df_filtered["Name Of Applicant"].str.contains(search_query, case=False)
        ]

    # -----------------------------------------------------------
    # JAVASCRIPT RENDERER (Inline Fix)
    # -----------------------------------------------------------
    # This script creates a self-contained button that builds the HTML 
    # and opens it in a new window immediately upon click.
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <button style="background-color: #d32f2f; color: white; border: none; 
                border-radius: 4px; cursor: pointer; padding: 4px 12px; font-weight: bold;">
                🖨️ PDF
                </button>
            `;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const d = params.data;
                const htmlContent = `
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap" rel="stylesheet">
                        <style>
                            body { font-family: 'Noto Sans Gujarati', sans-serif; padding: 40px; line-height: 1.5; }
                            .header { text-align: center; font-size: 22px; font-weight: bold; }
                            .subheader { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
                            table { width: 100%; border-collapse: collapse; }
                            td { border: 1px solid black; padding: 10px; }
                            .label { font-weight: bold; background: #f0f0f0; width: 30%; }
                            .sr-no { font-size: 24px; font-weight: bold; color: #d32f2f; }
                            .sketch { border: 1px solid black; height: 300px; margin-top: 20px; text-align:center; color:#ccc; padding-top:100px; font-size:30px; }
                        </style>
                    </head>
                    <body>
                        <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
                        <div class="subheader">સબ ડિવિઝન, વિરપુર</div>
                        <h3 style="text-align:center">સર્વે ફોર્મ (Survey Form)</h3>
                        <table>
                            <tr><td class="label">અરજદારનું નામ</td><td colspan="2">${d['Name Of Applicant'] || ''}</td></tr>
                            <tr><td class="label">સરનામું</td><td colspan="2">${d['Address1'] || ''} ${d['Address2'] || ''}, ${d['Village Or City'] || ''}</td></tr>
                            <tr><td class="label">SR Number</td><td class="sr-no">${d['SR Number'] || ''}</td><td>મોબાઈલ: ${d['Mobile Number'] || ''}</td></tr>
                            <tr><td class="label">લોડ વિગત</td><td colspan="2">${d['Demand Load'] || ''} ${d['Load Uom'] || ''} (${d['SR Type'] || ''})</td></tr>
                        </table>
                        <div class="sketch">નકશો (SKETCH)</div>
                        <script>
                            document.fonts.ready.then(() => { window.print(); });
                        </script>
                    </body>
                    </html>
                `;
                var printWindow = window.open('', '_blank');
                printWindow.document.write(htmlContent);
                printWindow.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    # -----------------------------------------------------------
    # GRID CONFIGURATION
    # -----------------------------------------------------------
    def show_grid(data, key):
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        
        # Add the Action Column
        gb.configure_column(
            "PDF_Print", 
            headerName="Action", 
            cellRenderer=render_print_button, 
            width=100, 
            pinned='left'
        )
        
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        gridOptions = gb.build()
        
        AgGrid(
            data, 
            gridOptions=gridOptions, 
            height=500, 
            theme="streamlit", 
            allow_unsafe_jscode=True, 
            key=key,
            reload_data=True
        )

    # -----------------------------------------------------------
    # DISPLAY STAGES
    # -----------------------------------------------------------
    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    # Stage 1: Filter Logic
    df_survey = df_filtered[
        (df_filtered["Survey Category"] == "") & 
        (df_filtered["SR Status"].str.upper() == "OPEN")
    ]

    with t1:
        st.info(f"📍 {len(df_survey)} SRs waiting for survey.")
        show_grid(df_survey, "survey_grid")

    with t2:
        df_est = df_filtered[
            (df_filtered["Survey Category"] != "") & 
            (df_filtered["Date Of Est Appr Launch"] == "")
        ]
        st.info(f"📍 {len(df_est)} SRs waiting for estimate.")
        show_grid(df_est, "est_grid")

else:
    st.info("👋 Please upload an Excel or CSV file to begin tracking.")
