from pathlib import Path

import streamlit as st

from contact_manager import ContactStore, validate_contact_fields


DATA_FILE = Path(__file__).parent / "contacts.json"
store = ContactStore(DATA_FILE)

st.set_page_config(page_title="Contacts", page_icon="C", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink: #1e2523; --muted: #6d7671; --accent: #d85b3f; --line: #dbe2dc; }
    html, body, [class*="css"] { font-family: Manrope, sans-serif; }
    .stApp { background: #f6f7f2; color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 980px; padding-top: 3rem; }
    .brand { display: flex; align-items: center; gap: 10px; color: var(--ink); font-size: 17px; font-weight: 800; letter-spacing: -.04em; }
    .brand-mark { display: inline-grid; place-items: center; width: 29px; height: 29px; margin-right: 8px; color: white; background: var(--ink); border-radius: 9px 9px 9px 2px; }
    .eyebrow { margin: 0 0 14px; color: var(--accent); font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: .11em; text-transform: uppercase; }
    h1 { font-size: 62px !important; line-height: .98 !important; letter-spacing: -.08em !important; }
    h2 { letter-spacing: -.06em !important; }
    .hero-copy { color: var(--muted); font-size: 15px; }
    .contact-card { min-height: 82px; padding: 17px; margin-bottom: 12px; background: white; border: 1px solid transparent; border-radius: 10px; }
    .contact-card:hover { border-color: var(--line); }
    .avatar { display: inline-grid; place-items: center; width: 45px; height: 45px; color: var(--ink); background: #dbe9dc; border-radius: 50%; font-weight: 800; }
    .contact-name { margin: 0; font-weight: 800; }
    .contact-phone { margin: 4px 0 0; color: var(--muted); font-family: 'DM Mono', monospace; font-size: 11px; }
    div.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); }
    .login-panel { max-width: 480px; margin: 8vh auto 0; padding: 2rem; background: white; border: 1px solid var(--line); border-radius: 14px; }
    @media (max-width: 650px) { h1 { font-size: 46px !important; } .block-container { padding: 2rem 1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def initials(name):
    return "".join(part[0] for part in name.split()[:2]).upper()


def login_page():
    st.markdown('<div class="login-panel">', unsafe_allow_html=True)
    st.markdown('<div class="brand"><span class="brand-mark">C</span> contacts</div>', unsafe_allow_html=True)
    st.markdown('<p class="eyebrow" style="margin-top: 4rem;">Welcome back</p>', unsafe_allow_html=True)
    st.title("Your people,\nright this way.")
    st.markdown('<p class="hero-copy">Sign in to open your personal directory.</p>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Enter contacts", type="primary", use_container_width=True)
    st.caption("Demo access: any email and password with 4+ characters.")
    st.markdown("</div>", unsafe_allow_html=True)
    if submitted:
        if not email.strip() or len(password) < 4:
            st.error("Enter a valid email and a password with at least 4 characters.")
        else:
            st.session_state.authenticated = True
            st.rerun()


@st.dialog("Add a contact")
def add_contact_dialog():
    with st.form("add_contact_form"):
        name = st.text_input("Full name", placeholder="e.g. Maya Angelou")
        phone = st.text_input("Phone number", placeholder="e.g. +1 555 0100")
        if st.form_submit_button("Save contact", type="primary", use_container_width=True):
            try:
                validate_contact_fields(name, phone)
                store.add(name, phone)
                st.session_state.notice = "Contact added."
                st.rerun()
            except ValueError as error:
                st.error(str(error))


@st.dialog("Edit contact")
def edit_contact_dialog(contact):
    with st.form("edit_contact_form"):
        name = st.text_input("Full name", value=contact["name"])
        phone = st.text_input("Phone number", value=contact["phone"])
        if st.form_submit_button("Save changes", type="primary", use_container_width=True):
            try:
                validate_contact_fields(name, phone)
                store.update(contact["id"], name, phone)
                st.session_state.notice = "Contact updated."
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def dashboard():
    contacts = store.load()
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown('<div class="brand"><span class="brand-mark">C</span> contacts</div>', unsafe_allow_html=True)
    with top_right:
        if st.button("Sign out"):
            st.session_state.authenticated = False
            st.rerun()

    st.write("")
    hero_left, hero_right = st.columns([3, 1])
    with hero_left:
        st.markdown('<p class="eyebrow">Personal directory</p>', unsafe_allow_html=True)
        st.title("Keep your people\nclose at hand.")
        st.markdown('<p class="hero-copy">A calm, simple place for the people you reach most.</p>', unsafe_allow_html=True)
    with hero_right:
        st.write("")
        if st.button("＋ Add contact", type="primary", use_container_width=True):
            add_contact_dialog()

    st.divider()
    search = st.text_input("Search contacts", placeholder="Search by name or phone", label_visibility="collapsed")
    filtered_contacts = [
        contact for contact in contacts
        if search.strip().casefold() in f"{contact['name']} {contact['phone']}".casefold()
    ]
    st.subheader(f"{len(contacts)} contact{'s' if len(contacts) != 1 else ''}")

    if not filtered_contacts:
        st.info("No contacts found. Add your first contact to get started.")
        return

    for contact in filtered_contacts:
        left, details, actions = st.columns([1, 6, 2])
        with left:
            st.markdown(f'<div class="avatar">{initials(contact["name"])}</div>', unsafe_allow_html=True)
        with details:
            st.markdown(f'<p class="contact-name">{contact["name"]}</p><p class="contact-phone">{contact["phone"]}</p>', unsafe_allow_html=True)
        with actions:
            edit_col, delete_col = st.columns(2)
            with edit_col:
                if st.button("Edit", key=f"edit-{contact['id']}"):
                    edit_contact_dialog(contact)
            with delete_col:
                if st.button("Delete", key=f"delete-{contact['id']}"):
                    store.delete(contact["id"])
                    st.session_state.notice = "Contact deleted."
                    st.rerun()
        st.divider()

    if st.session_state.get("notice"):
        st.success(st.session_state.pop("notice"))


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    dashboard()
else:
    login_page()