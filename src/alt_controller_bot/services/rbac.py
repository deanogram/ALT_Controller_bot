from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    ANALYST = "analyst"

    @classmethod
    def hierarchy(cls) -> dict["Role", set["Role"]]:
        return {
            cls.OWNER: {cls.OWNER, cls.ADMIN, cls.EDITOR, cls.ANALYST},
            cls.ADMIN: {cls.ADMIN, cls.EDITOR, cls.ANALYST},
            cls.EDITOR: {cls.EDITOR},
            cls.ANALYST: {cls.ANALYST},
        }

    def can(self, required: "Role") -> bool:
        return required in self.hierarchy()[self]


class PermissionError(Exception):
    pass


def ensure_role(role: Role, required: Role) -> None:
    if not role.can(required):
        raise PermissionError(f"Role {role} lacks permission for {required}")
