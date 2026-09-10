import argparse
import json
import sys
import uuid
from pathlib import Path


class ContactStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                contacts = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(f"Contact file is not valid JSON: {error}") from error
        if not isinstance(contacts, list):
            raise ValueError("Contact file must contain a JSON list")
        return contacts

    def save(self, contacts):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(contacts, file, indent=2)
            file.write("\n")
        temporary_path.replace(self.path)

    def add(self, name, phone):
        contacts = self.load()
        contact = {"id": uuid.uuid4().hex[:8], "name": name.strip(), "phone": phone.strip()}
        contacts.append(contact)
        self.save(contacts)
        return contact

    def search(self, query):
        normalized_query = query.strip().casefold()
        return [
            contact
            for contact in self.load()
            if normalized_query in contact["name"].casefold()
            or normalized_query in contact["phone"].casefold()
        ]

    def update(self, contact_id, name=None, phone=None):
        contacts = self.load()
        for contact in contacts:
            if contact["id"] == contact_id:
                if name is not None:
                    contact["name"] = name.strip()
                if phone is not None:
                    contact["phone"] = phone.strip()
                self.save(contacts)
                return contact
        return None

    def delete(self, contact_id):
        contacts = self.load()
        remaining_contacts = [contact for contact in contacts if contact["id"] != contact_id]
        if len(remaining_contacts) == len(contacts):
            return False
        self.save(remaining_contacts)
        return True


def validate_contact_fields(name, phone):
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")
    if not phone or not phone.strip():
        raise ValueError("Phone number cannot be empty")


def print_contacts(contacts):
    if not contacts:
        print("No contacts found.")
        return
    print(f"{'ID':<10} {'NAME':<28} PHONE")
    print("-" * 56)
    for contact in contacts:
        print(f"{contact['id']:<10} {contact['name']:<28} {contact['phone']}")


def build_parser():
    parser = argparse.ArgumentParser(description="Maintain a local contact list.")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path("contacts.json"),
        help="JSON file used for storage (default: contacts.json)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Add a contact")
    add_parser.add_argument("name")
    add_parser.add_argument("phone")

    search_parser = commands.add_parser("search", help="Search by name or phone")
    search_parser.add_argument("query")

    commands.add_parser("list", help="Display all contacts")

    update_parser = commands.add_parser("update", help="Update a contact by ID")
    update_parser.add_argument("contact_id")
    update_parser.add_argument("--name")
    update_parser.add_argument("--phone")

    delete_parser = commands.add_parser("delete", help="Delete a contact by ID")
    delete_parser.add_argument("contact_id")

    return parser


def run(args):
    store = ContactStore(args.file)
    if args.command == "add":
        validate_contact_fields(args.name, args.phone)
        contact = store.add(args.name, args.phone)
        print(f"Added {contact['name']} ({contact['id']}).")
    elif args.command == "search":
        print_contacts(store.search(args.query))
    elif args.command == "list":
        print_contacts(store.load())
    elif args.command == "update":
        if args.name is None and args.phone is None:
            raise ValueError("Provide --name, --phone, or both")
        if args.name is not None and not args.name.strip():
            raise ValueError("Name cannot be empty")
        if args.phone is not None and not args.phone.strip():
            raise ValueError("Phone number cannot be empty")
        contact = store.update(args.contact_id, args.name, args.phone)
        if contact is None:
            raise ValueError(f"No contact found with ID {args.contact_id}")
        print(f"Updated {contact['name']} ({contact['id']}).")
    elif args.command == "delete":
        if not store.delete(args.contact_id):
            raise ValueError(f"No contact found with ID {args.contact_id}")
        print(f"Deleted contact {args.contact_id}.")


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        run(args)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()