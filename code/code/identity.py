"""Identity Resolution Engine.

Resolves subject identities across current profiles and historical audit logs.
Extracts stable user_ids, aliases, phone numbers, names, and email hashes.
"""

from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Set


@dataclass
class IdentityProfile:
    user_id: str
    name: str
    primary_email: str
    primary_phone: str
    primary_hash: str
    all_emails: Set[str] = field(default_factory=set)
    all_names: Set[str] = field(default_factory=set)
    all_phones: Set[str] = field(default_factory=set)
    all_hashes: Set[str] = field(default_factory=set)

    def matches(self, identifier: Optional[str]) -> bool:
        if not identifier:
            return False
        ident_clean = identifier.strip().lower()
        if not ident_clean:
            return False
        
        # Check direct matches
        if ident_clean == self.user_id.lower():
            return True
        if ident_clean in self.all_emails:
            return True
        if ident_clean in self.all_hashes:
            return True
        
        # Phone match (normalize phone: remove spaces and hyphens)
        clean_phone = re_clean_phone(ident_clean)
        if clean_phone and len(clean_phone) >= 7:
            for p in self.all_phones:
                if clean_phone == re_clean_phone(p):
                    return True
        
        return False


def re_clean_phone(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


class IdentityResolver:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir
        self.users_by_id: Dict[str, IdentityProfile] = {}
        self.email_to_uid: Dict[str, str] = {}
        self._load_identities()
        self._load_audit_logs()

    def _load_identities(self) -> None:
        ident_file = os.path.join(self.dataset_dir, "user_identities.csv")
        with open(ident_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row["user_id"]
                email = row["email"].lower().strip()
                name = row["name"].strip()
                phone = row["phone"].strip()
                email_hash = row["email_hash"].lower().strip() if row["email_hash"] else ""

                profile = IdentityProfile(
                    user_id=uid,
                    name=name,
                    primary_email=email,
                    primary_phone=phone,
                    primary_hash=email_hash,
                )
                profile.all_emails.add(email)
                if name:
                    profile.all_names.add(name)
                if phone:
                    profile.all_phones.add(phone)
                if email_hash:
                    profile.all_hashes.add(email_hash)
                
                # Also compute SHA-256 of primary email if missing
                computed_hash = hashlib.sha256(email.encode("utf-8")).hexdigest().lower()
                profile.all_hashes.add(computed_hash)

                self.users_by_id[uid] = profile
                self.email_to_uid[email] = uid

    def _load_audit_logs(self) -> None:
        audit_file = os.path.join(self.dataset_dir, "user_audit_log.csv")
        if not os.path.exists(audit_file):
            return

        with open(audit_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row["user_id"]
                field_name = row["field_name"]
                old_val = row["old_value"].strip()
                new_val = row["new_value"].strip()

                if uid not in self.users_by_id:
                    # Create empty profile if not found in current identities
                    self.users_by_id[uid] = IdentityProfile(
                        user_id=uid,
                        name="",
                        primary_email="",
                        primary_phone="",
                        primary_hash="",
                    )

                profile = self.users_by_id[uid]

                if field_name == "email":
                    if old_val:
                        old_lower = old_val.lower()
                        profile.all_emails.add(old_lower)
                        self.email_to_uid[old_lower] = uid
                        profile.all_hashes.add(hashlib.sha256(old_lower.encode("utf-8")).hexdigest().lower())
                    if new_val:
                        new_lower = new_val.lower()
                        profile.all_emails.add(new_lower)
                        self.email_to_uid[new_lower] = uid
                        profile.all_hashes.add(hashlib.sha256(new_lower.encode("utf-8")).hexdigest().lower())

                elif field_name == "email_hash":
                    if old_val:
                        profile.all_hashes.add(old_val.lower())
                    if new_val:
                        profile.all_hashes.add(new_val.lower())

                elif field_name == "phone":
                    if old_val:
                        profile.all_phones.add(old_val)
                    if new_val:
                        profile.all_phones.add(new_val)

                elif field_name == "name":
                    if old_val:
                        profile.all_names.add(old_val)
                    if new_val:
                        profile.all_names.add(new_val)

    def resolve(self, email: str) -> Optional[IdentityProfile]:
        email_clean = email.lower().strip()
        uid = self.email_to_uid.get(email_clean)
        if uid and uid in self.users_by_id:
            return self.users_by_id[uid]
        return None
