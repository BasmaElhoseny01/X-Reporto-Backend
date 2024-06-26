from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class StatusEnum(str, Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"

class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class OccupationEnum(str, Enum):
    doctor = "doctor"
    employee = "employee"

class ResultTypeEnum(str, Enum):
    template = "template"
    llm = "llm"
    custom = "custom"

class ActivityEnum(str, Enum):
    view = "view"
    edit = "edit"
    delete = "delete"
    create = "create"
    assign = "assign"
    unassign = "unassign"
    archive = "archive"
    unarchive = "unarchive"