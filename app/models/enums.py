from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class StatusEnum(str, Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"

class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class ResultTypeEnum(str, Enum):
    template = "template"
    llm = "llm"
    custom = "custom"