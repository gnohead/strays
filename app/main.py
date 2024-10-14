#!python3
#-*- coding: utf-8 -*-

from datetime import datetime

import streamlit as st

import core
import authentication as auth

TITLE = "Strays"
ICON = "🐈"

def main():
    st.set_page_config(page_title=TITLE, page_icon=ICON, layout="wide")

    if core.is_first():
        core.initialize()
        auth.initialize()

    if auth.get_status():
        st.switch_page("pages/home.py")
    else:
        st.title("CompuMath AI")
        auth.show_login(location="main")



if __name__ == "__main__":
    main()
    print(f">>>> rerun ({datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]})")

