#!python3
#-*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path

import streamlit as st
from menu import show_menu

from textwrap import dedent

TITLE = "Home."
ICON =  "🏠"

def show_page():
    st.set_page_config(page_title=TITLE, page_icon=ICON, layout="wide")
    show_menu()
    
    st.write("Hello!")


def page():
    return { 
        "page" : f"pages/{Path(__file__).resolve().name}",
        "label" : TITLE,
        "icon" : ICON
    }


if __name__ == "__main__":
    show_page()
    print(f">>>> rerun ({datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]})")
