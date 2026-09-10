# Contact Management System

A Streamlit-hosted contact manager with a login screen, modal add/edit forms, search, delete, and a dependency-free command-line version. Both interfaces use the shared `contacts.json` file.

## Streamlit app

Install the Streamlit dependency and start the Python-hosted version:

```text
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Then open the URL shown by Streamlit, usually `http://localhost:8501`.

The local demo accepts any email address and a password with at least four characters. Production authentication requires a server-side identity system.

## Requirements

- Python 3.9 or newer

## Usage

Run commands from this folder:

```text
python contact_manager.py add "Ada Lovelace" "555-0100"
python contact_manager.py list
python contact_manager.py search ada
python contact_manager.py update CONTACT_ID --phone "555-0199"
python contact_manager.py delete CONTACT_ID
```

Use another storage file with `--file`, placed before the command:

```text
python contact_manager.py --file data/my-contacts.json add "Grace Hopper" "555-0110"
```

Run the tests with:

```text
python -m unittest discover -p "test_*.py"
```