#!python3
#-*- coding: utf-8 -*-

import streamlit as st
import authentication as auth

def authenticated_menu():
    from pages import home
    from pages import risk_aversion_evaluator
    from pages import consultant


    st.sidebar.markdown(f"## **{auth.get_username()}**")
    auth.show_logout(location="sidebar")
    st.sidebar.html("<hr>")

    st.sidebar.markdown("## Applications")
    st.sidebar.page_link(**home.page())
    st.sidebar.page_link(**risk_aversion_evaluator.page())
    st.sidebar.page_link(**consultant.page())


def show_menu():
    if auth.get_status():
        authenticated_menu()
    else:
        st.switch_page("main.py")

