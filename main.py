# gsheets-app.py
from __future__ import annotations


import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def gs_append(
    self,
    *,  # keyword-only arguments:
    spreadsheet: Optional[Union[str, Spreadsheet]] = None,
    worksheet: Optional[Union[str, int, Worksheet]] = None,
    data: Optional[Union[DataFrame, ndarray, List[list], List[dict]]] = None,
    folder_id: Optional[str] = None,
) -> DataFrame | None:
    if not spreadsheet and self._spreadsheet:
        spreadsheet = self._spreadsheet
    if not folder_id and self._worksheet:
        folder_id = self._worksheet

    if isinstance(spreadsheet, str):
        spreadsheet = self._open_spreadsheet(spreadsheet=spreadsheet, folder_id=folder_id)

    worksheet_id = self._instance._select_worksheet(spreadsheet=spreadsheet, folder_id=folder_id, worksheet=worksheet)

    if worksheet_id:
        worksheet_id.append_rows(values=data.values.tolist(), value_input_option='USER_ENTERED')

    return data


# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

temp_df = conn.read(
    worksheet="Form",
    ttl="1s"
)


with st.form("Add observation", clear_on_submit=True):
    col_observation, col_student = st.columns([80, 20])
    with col_observation:
        observation = st.text_input("Observation", placeholder="Write your observation")
    with col_student:
        student = st.selectbox("Student", ["Anna", "Eduard", "Mercè", "Miquel"])
    col_what, col_who = st.columns([50, 50])
    with col_what:
        what = st.radio("What?", ["Procedure", "Start", "End", "Enters", "Exists"])
    with col_who:
        who = st.radio("Who?", ["Patient", "Doctor", "Nurse", "Technician", "Porter", "Assistant", "Other"])
    submit = st.form_submit_button("Save")

    if submit:
        new_data = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                  "what": what,
                                  "who": who,
                                  "observation": observation,
                                  "student": student}])
        data = gs_append(
                    conn,
                    worksheet="Form",
                    data=new_data
                )
        temp_df = pd.concat([temp_df, data], ignore_index=True)

st.write(temp_df.iloc[::-1])

