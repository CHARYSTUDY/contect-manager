import json
import tempfile
import unittest
from pathlib import Path

from contact_manager import ContactStore, validate_contact_fields


class ContactManagerTests(unittest.TestCase):
    def test_contact_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ContactStore(Path(directory) / "contacts.json")

            contact = store.add("Ada Lovelace", "555-0100")
            self.assertEqual(store.load(), [contact])
            self.assertEqual(store.search("ada"), [contact])
            self.assertEqual(store.search("0100"), [contact])

            updated = store.update(contact["id"], phone="555-0199")
            self.assertEqual(updated["phone"], "555-0199")
            self.assertEqual(store.load()[0]["phone"], "555-0199")

            self.assertTrue(store.delete(contact["id"]))
            self.assertEqual(store.load(), [])
            self.assertFalse(store.delete(contact["id"]))

    def test_store_loads_existing_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contacts.json"
            path.write_text(json.dumps([{"id": "abc123", "name": "Grace Hopper", "phone": "555-0110"}]))

            self.assertEqual(ContactStore(path).search("grace")[0]["id"], "abc123")

    def test_contact_fields_are_required(self):
        for name, phone in [("", "555-0100"), ("Ada", "")]:
            with self.assertRaises(ValueError):
                validate_contact_fields(name, phone)