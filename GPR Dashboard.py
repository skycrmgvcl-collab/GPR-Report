import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.markdown("---")

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df_raw = pd.read_excel(file)

    # Clean data
    df_raw.columns = df_raw.columns.str.strip()
    for col in df_raw.columns:
        df_raw[col] = df_raw[col].astype(str).str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT'], "")

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    unique_schemes = sorted([x for x in df_raw["Name Of Scheme"].unique() if x != ""])
    sel_schemes = st.sidebar.multiselect("Scheme", unique_schemes, default=unique_schemes)
    unique_types = sorted([x for x in df_raw["SR Type"].unique() if x != ""])
    sel_types = st.sidebar.multiselect("SR Type", unique_types, default=unique_types)
    search_query = st.sidebar.text_input("Search SR or Name")

    # Apply global filters
    df_filtered = df_raw[(df_raw["Name Of Scheme"].isin(sel_schemes)) & (df_raw["SR Type"].isin(sel_types))].copy()
    if search_query:
        df_filtered = df_filtered[df_filtered["SR Number"].str.contains(search_query, case=False) | 
                                  df_filtered["Name Of Applicant"].str.contains(search_query, case=False)]

    # JavaScript for Survey Print (Kept exactly as you liked)
    render_print_button = JsCode("""
    class PrintRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `<button style="background-color: #2e7d32; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 10px; font-weight: bold;">🖨️ PDF Form</button>`;
            this.btn = this.eGui.querySelector('button');
            this.btn.addEventListener('click', () => {
                const r = params.data;
                const htmlContent = `<html><head><meta charset="UTF-8"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap" rel="stylesheet"><style>@page { size: A4; margin: 5mm; } body { font-family: 'Noto Sans Gujarati', sans-serif; font-size: 13px; margin: 0; padding: 20px; } .header { text-align: center; font-size: 20px; font-weight: bold; } .title { text-align: center; font-size: 16px; font-weight: bold; text-decoration: underline; margin: 10px 0; } table { width: 100%; border-collapse: collapse; } td { border: 1px solid black; padding: 6px; } .sketch { height: 320px; border: 1px solid black; } .srno { font-weight: bold; font-size: 17px; color: #d32f2f; }</style></head><body><div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div><div class="title">Survey Form</div><table><tr><td colspan="2">તારીખ :- __________</td><td colspan="2" style="text-align:right">2026</td></tr><tr><td>૧. નામ</td><td colspan="3">${r['Name Of Applicant'] || ''}</td></tr><tr><td>૨. સરનામું</td><td colspan="3">${r['Address1'] || ''} ${r['Village Or City'] || ''}</td></tr><tr><td>૩. SR No</td><td class="srno">${r['SR Number'] || ''}</td><td>ફોન</td><td>${r['Mobile Number'] || ''}</td></tr><tr><td>૪. લોડ</td><td colspan="3">${r['Demand Load'] || ''} ${r['Load Uom'] || ''}</td></tr><tr><td colspan="4"><b>સર્વે વિગતો</b></td></tr><tr><td colspan="4"><div class="sketch"></div></td></tr></table><script>document.fonts.ready.then(() => { window.print(); });</script></body></html>`;
                var w = window.open('', '_blank'); w.document.write(htmlContent); w.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    def show_grid(data, key, can_print=False):
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        if can_print:
            gb.configure_column("Print", headerName="Action", cellRenderer=render_print_button, width=110, pinned='left')
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        AgGrid(data, gridOptions=gb.build(), height=500, theme="streamlit", allow_unsafe_jscode=True, key=key, reload_data=True)

    # Tabs
    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    with t1:
        df_survey = df_filtered[(df_filtered["Survey Category"] == "") & (df_filtered["SR Status"].str.upper() == "OPEN")]
        st.write(f"Total: {len(df_survey)}")
        show_grid(df_survey, "grid_survey", can_print=True)

    with t2:
        # LOGIC: Survey done (Category exists) but Estimate not launched
        df_est = df_filtered[
            (df_filtered["Survey Category"] != "") & 
            (df_filtered["Date Of Est Appr Launch"] == "") &
            (df_filtered["SR Status"].str.upper() == "OPEN")
        ]
        st.write(f"Total: {len(df_est)}")
        show_grid(df_est, "grid_estimate")

    with t3:
        # LOGIC: Estimate launched but FQ not issued
        df_fq = df_filtered[
            (df_filtered["Date Of Est Appr Launch"] != "") & 
            (df_filtered["Date Of FQ Issued"] == "") &
            (df_filtered["SR Status"].str.upper() == "OPEN")
        ]
        st.write(f"Total: {len(df_fq)}")
        show_grid(df_fq, "grid_fq")

else:
    st.info("Please upload your file.")
