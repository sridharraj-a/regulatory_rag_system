"""
styles.py

Contains all Streamlit styling.
"""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """
    Apply custom CSS to the Streamlit application.
    """

    st.markdown(
        """
<style>

/* --------------------------------------------------
Google Font
-------------------------------------------------- */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html,
body,
[class*="css"],
.stApp{
    font-family: 'Inter', sans-serif;
}


/* --------------------------------------------------
Main Layout
-------------------------------------------------- */

.block-container{
    padding-top:2rem;
    padding-left:3rem;
    padding-right:3rem;
    padding-bottom:2rem;
}


/* --------------------------------------------------
Title
-------------------------------------------------- */

h1{
    font-size:34px !important;
    font-weight:700 !important;
    color:#0f172a;
}


/* --------------------------------------------------
Headers
-------------------------------------------------- */

h2{
    font-size:24px;
    font-weight:600;
}

h3{
    font-size:20px;
    font-weight:600;
}


/* --------------------------------------------------
Sidebar
-------------------------------------------------- */

section[data-testid="stSidebar"]{
    width:330px;
}

section[data-testid="stSidebar"] h1{
    font-size:24px !important;
}


/* --------------------------------------------------
Chat Messages
-------------------------------------------------- */

[data-testid="stChatMessage"]{
    padding: 0.75rem 0;
    margin-bottom: 1rem;
    border: none;
    background: transparent;
}


/* --------------------------------------------------
Buttons
-------------------------------------------------- */

.stButton>button{

    width:100%;

    border-radius:8px;

    height:42px;

    font-weight:600;

}


/* --------------------------------------------------
Text Input
-------------------------------------------------- */

.stChatInputContainer{

    padding-top:20px;

}


/* --------------------------------------------------
Progress Bar
-------------------------------------------------- */

.stProgress{

    margin-top:8px;

    margin-bottom:8px;

}


/* --------------------------------------------------
Expanders
-------------------------------------------------- */

.streamlit-expanderHeader{

    font-weight:600;

    font-size:16px;

}


/* --------------------------------------------------
Code Blocks
-------------------------------------------------- */

pre{

    border-radius:8px;

}


/* --------------------------------------------------
Success / Info / Warning
-------------------------------------------------- */

.stAlert{

    border-radius:10px;

}


/* --------------------------------------------------
Scrollbar
-------------------------------------------------- */

::-webkit-scrollbar{

    width:10px;

}

::-webkit-scrollbar-thumb{

    background:#C9CDD2;

    border-radius:10px;

}


/* --------------------------------------------------
Tables
-------------------------------------------------- */

table{

    font-size:15px;

}


/* --------------------------------------------------
Footer
-------------------------------------------------- */

footer{

    visibility:hidden;

}


/* --------------------------------------------------
Deploy Button
-------------------------------------------------- */

[data-testid="stDecoration"]{

    display:none;

}


/* --------------------------------------------------
Toolbar
-------------------------------------------------- */

#MainMenu{

    visibility:hidden;

}

header[data-testid="stHeader"]{
    background: transparent;
    height: 3rem;
}

</style>
""",
        unsafe_allow_html=True,
    )
