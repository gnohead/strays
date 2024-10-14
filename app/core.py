#!python3
#-*- coding: utf-8 -*-

import os, sys
from pathlib import Path

import streamlit as st

ROOT = lambda pt: Path(os.path.commonpath([__file__, sys.executable])).joinpath(pt).resolve()

def get_session_state():
    return st.session_state
