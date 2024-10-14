#!python3
#-*- coding: utf-8 -*-

"""ref: https://github.com/mkhorasani/Streamlit-Authenticator"""

from datetime import datetime

from core import ROOT
from core import get_session_state

AUTH_ROOT = lambda pt: ROOT("auth").joinpath(pt).resolve()

import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

from typing import Literal

def initialize():
    sst = get_session_state()

    authfile = AUTH_ROOT("users.yaml")

    with open(authfile) as file:
        configs = yaml.load(file, Loader=SafeLoader)

    # Pres-hashing all plain text passwords once
    # 기본으로 자동으로 되지만, 사용자가 많으면 수동으로 하는 것을 권장
    # 이 때, Authenticate 클래스의 auto_hash 파라메터를 False로 설정 
    stauth.Hasher.hash_passwords(configs["credentials"])

    sst.authenticator = stauth.Authenticate(**configs, auto_hash=False)

    print("authentication initilized.")

def get_status():
    sst = get_session_state()
    return sst.get("authentication_status", None)

def get_name():
    sst = get_session_state()
    return sst.get("name", None)

def get_username():
    sst = get_session_state()
    return sst.get("username", None)

def get_email():
    sst = get_session_state()
    return sst.get("email", None)


def show_login(location:Literal["main", "sidebar"]):
    sst = get_session_state()

    try:
        sst.authenticator.login(key="Login", location=location, max_login_attempts=5)

        if get_status() is False:
            st.error('Username/password is incorrect')

        elif get_status() is None:
            st.warning('Please enter your username and password')
    
    except Exception as e:
        st.error(e)

def show_logout(location:Literal["main", "sidebar"]):
    sst = get_session_state()

    try:
        if get_status():
            sst.authenticator.logout(key="Logout", location=location)
        
    except Exception as e:
        st.error(e)


if __name__ == "__main__":
    initialize()
    if get_status() is not None:
        show_logout()
    else:
        show_login()
    print(f">>>> rerun ({datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]})")
