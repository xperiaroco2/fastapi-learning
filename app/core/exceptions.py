import uuid


class DomainException(Exception):
    pass


class EntityNotFoundError(DomainException):
    def __init__(self, entity_name: str, entity_id: uuid.UUID):
        self.entity_name = entity_name
        self.entity_id = entity_id
        self.message = f"{entity_name} with id {entity_id} not found"
        super().__init__(self.message)


class EntityAlreadyExistsError(DomainException):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"{entity_name} with {field_name} '{field_value}' already exists"
        super().__init__(self.message)
