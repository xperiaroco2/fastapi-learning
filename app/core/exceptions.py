import uuid


class DomainException(Exception):
    pass


class EntityNotFoundError(DomainException):
    def __init__(self, entity_name: str, entity_field: str, entity_value: uuid.UUID | str | int):
        self.entity_name = entity_name
        self.entity_field = entity_field
        self.entity_value = entity_value
        self.message = f"{entity_name} with {entity_field} {entity_value} not found"
        super().__init__(self.message)


class EntityAlreadyExistsError(DomainException):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"{entity_name} with {field_name} '{field_value}' already exists"
        super().__init__(self.message)


class EntityUnauthorizedError(DomainException):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"{entity_name} with {field_name} '{field_value}' unauthorized to proceed this action"
        super().__init__(self.message)
