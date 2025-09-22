# bbmsapp.py
import streamlit as st
import os
import pandas as pd
from utils import init_env
print("***************")
import pipeline 
from pipeline.llm import get_roast_llm
from pipeline.prompt_template import get_roast_prompt
print("******* No Error ********")
print("*******## at  import get_parser ********")
from pipeline.parser import get_roast_parser
print("*******## done  import get_parser ********")
from pipeline.wrapper import roast_one


# Load .env (if present)
init_env()

from pipeline.alias_lookup import build_alias_index, resolve_name
from pathlib import Path
from config import PROJECT_ROOT

DATA_PATH = PROJECT_ROOT/"bbms_2003.csv" 


import pandas as pd

def read_roster_csv(path: str) -> pd.DataFrame:
    # 1) Try UTF-8 first
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        pass
    # 2) Try Windows-1252 (common on Excel/Windows)
    try:
        return pd.read_csv(path, encoding="cp1252")
    except UnicodeDecodeError:
        pass
    # 3) Last resort: latin-1 (lossy but won’t error)
    return pd.read_csv(path, encoding="latin-1")



@st.cache_data(show_spinner=False)
def load_roster(path: str):
    df = read_roster_csv(path)
    # Normalize headers and coerce to string for safety in UI
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str)
    # ... then build alias index etc.
    expected = {'name', 'original_name', 'commonly_called', 'roast_level',
       'about_person', 'dark_joke_level', 'joke_scinareo', 'in5years'}
    missing = expected - set(df.columns) 
    print("******************")  
    print(missing) 
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    alias_to_row, row_to_aliases = build_alias_index(df, name_col="name")
    return df, alias_to_row, row_to_aliases

roster_df, alias_to_row, row_to_aliases = load_roster(DATA_PATH)

print(alias_to_row)
print(row_to_aliases)


st.header("🎉 BBMS 2003 Batch Roasting GPT 🎉")

st.header("Let GenAI Roast your Friend")

st.warning("For now, the roaster is live for Guddi Devudu, Dabba aka Ashwin, Shiva, and Shashi — the rest go live by Oct 4. ")
query_name = st.text_input("Enter a classmate name or nickname: Ex: Dabba , Guddi , Devudu")
# query_name = 'ashwin gatadi'
if st.button("Find")  :
    idx, matched_alias, score = resolve_name(
        query=query_name,
        df=roster_df,
        alias_to_row=alias_to_row,
        row_to_aliases=row_to_aliases,
        name_col="name",
        threshold=70,
    )
    if idx is None:
        st.warning("No match. Wait till Oct 4th to roast everyone.")
    else:
        row = roster_df.iloc[idx]
        print("****** row  *******")
        row_to_dict =row.to_dict()
        st.success(f"Matched: {query_name} with  {row_to_dict['original_name']}")
        row_to_dict =row.to_dict()
        print(row_to_dict)
        st.write(f"You want GenAi to roast {query_name}, "
      f"This person is most commonly known as {row_to_dict['commonly_called']}")
    
        # st.write("Joke scenarios:", row["joke_scinareo"])
        # st.write("In 5 years:", row["in5years"])

        # TODO: When roast pipeline is ready, call it like:
       # bbmsapp.py (in the button handler after resolving row)
        result = roast_one(
            about=row["about_person"],
            joke_scenarios=row["joke_scinareo"],
            in5years=row["in5years"],
            roast_level=int(row.get("roast_level", 50)),
            dark_joke_level=int(row.get("dark_joke_level", 30)),
            original_name=row.get("original_name", ""),
            commonly_called=row.get("commonly_called", ""),
        )

        st.subheader("What I think about this Person")
        st.write(result.summary_funny)
        st.subheader("Jokes on him")
        for j in result.dark_jokes:
            st.write("•", j)
        st.subheader("Five-year Forecast")
        st.write(result.five_year_forecast)


