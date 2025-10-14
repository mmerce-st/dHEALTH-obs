# Copyright (c) Mercè Martín
# All rights reserved.
# This software is proprietary and confidential and may not under
# any circumstances be used, copied, or distributed.

from __future__ import annotations


import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


STUDENTS = ["Anna", "Eduard", "Mercè", "Miquel"]
WHAT = [None, "Procedure", "Incident", "Complication", "Start", "End", "Enters", "Exits"]
WHO = [None, "Patient", "Doctor", "Nurse", "Technician", "Porter", "Assistant", "Other"]
MAX_OBSERVATIONS = 25


st.markdown(
        """
    <style>
        div[role=radiogroup] label:first-of-type {
            visibility: hidden;
            height: 0px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


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

if "student" not in st.session_state:
    st.session_state.student = 0

st.markdown("### Observations")

with st.form("Add observation", clear_on_submit=True):
    col_observation, col_student = st.columns([80, 20])
    with col_observation:
        observation = st.text_input("Observation", placeholder="Write your observation")
    with col_student:
        student = st.selectbox("Student", STUDENTS, index=st.session_state.student)
    col_what, col_who, col_submit = st.columns([40, 40, 20])
    with col_what:
        what = st.radio("What?", WHAT)
    with col_who:
        who = st.radio("Who?", WHO)
    with col_submit:
        submit = st.form_submit_button("Save")

    if submit:
        st.session_state.student = STUDENTS.index(student)
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

col1, col2 = st.columns([50, 50])
with col1:
    st.write("Total number of observations:", len(temp_df))
with col2:
    st.write("Showing last", min([len(temp_df), MAX_OBSERVATIONS]))
st.write(temp_df.iloc[::-1][0: MAX_OBSERVATIONS])

