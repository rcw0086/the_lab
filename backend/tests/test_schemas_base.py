"""Tests for base schema classes."""

import pytest
from pydantic import ValidationError

from the_lab.schemas.base import (
    CreateSchema,
    ErrorDetail,
    ErrorResponse,
    ReadSchema,
    UpdateSchema,
)


# --- Concrete subclasses for testing ---


class ItemCreate(CreateSchema):
    name: str
    value: int | None = None


class ItemRead(ReadSchema):
    name: str
    value: int | None = None


class ItemUpdate(UpdateSchema):
    name: str | None = None
    value: int | None = None


# --- CreateSchema tests ---


class TestCreateSchema:
    def test_basic_creation(self) -> None:
        item = ItemCreate(name="test", value=42)
        assert item.name == "test"
        assert item.value == 42

    def test_optional_field_defaults_to_none(self) -> None:
        item = ItemCreate(name="test")
        assert item.value is None

    def test_strips_whitespace(self) -> None:
        item = ItemCreate(name="  padded  ", value=1)
        assert item.name == "padded"

    def test_from_attributes(self) -> None:
        class FakeORM:
            name = "from_orm"
            value = 10

        item = ItemCreate.model_validate(FakeORM())
        assert item.name == "from_orm"
        assert item.value == 10

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(value=1)  # type: ignore[call-arg]
        assert "name" in str(exc_info.value)


# --- ReadSchema tests ---


class TestReadSchema:
    def test_basic_read(self) -> None:
        item = ItemRead(id=1, name="test", value=42)
        assert item.id == 1
        assert item.name == "test"
        assert item.value == 42

    def test_missing_id_raises(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ItemRead(name="test")  # type: ignore[call-arg]
        assert "id" in str(exc_info.value)

    def test_optional_field_defaults_to_none(self) -> None:
        item = ItemRead(id=1, name="test")
        assert item.value is None

    def test_from_attributes(self) -> None:
        class FakeORM:
            id = 1
            name = "orm_item"
            value = 5

        item = ItemRead.model_validate(FakeORM())
        assert item.id == 1
        assert item.name == "orm_item"
        assert item.value == 5

    def test_serialization_roundtrip(self) -> None:
        item = ItemRead(id=1, name="test", value=42)
        data = item.model_dump()
        restored = ItemRead.model_validate(data)
        assert restored == item


# --- UpdateSchema tests ---


class TestUpdateSchema:
    def test_partial_update(self) -> None:
        item = ItemUpdate(name="new_name")
        assert item.name == "new_name"
        assert item.value is None

    def test_empty_update(self) -> None:
        item = ItemUpdate()
        assert item.name is None
        assert item.value is None

    def test_strips_whitespace(self) -> None:
        item = ItemUpdate(name="  padded  ")
        assert item.name == "padded"

    def test_from_attributes(self) -> None:
        class FakeORM:
            name = "updated"
            value = 99

        item = ItemUpdate.model_validate(FakeORM())
        assert item.name == "updated"
        assert item.value == 99


# --- ErrorDetail tests ---


class TestErrorDetail:
    def test_with_field(self) -> None:
        detail = ErrorDetail(field="username", message="already taken")
        assert detail.field == "username"
        assert detail.message == "already taken"

    def test_without_field(self) -> None:
        detail = ErrorDetail(message="internal error")
        assert detail.field is None
        assert detail.message == "internal error"

    def test_missing_message_raises(self) -> None:
        with pytest.raises(ValidationError):
            ErrorDetail()  # type: ignore[call-arg]


# --- ErrorResponse tests ---


class TestErrorResponse:
    def test_single_error(self) -> None:
        resp = ErrorResponse(
            error="not_found",
            detail=[ErrorDetail(message="Resource not found")],
        )
        assert resp.error == "not_found"
        assert len(resp.detail) == 1
        assert resp.detail[0].message == "Resource not found"

    def test_validation_errors(self) -> None:
        resp = ErrorResponse(
            error="validation_error",
            detail=[
                ErrorDetail(field="name", message="required"),
                ErrorDetail(field="value", message="must be positive"),
            ],
        )
        assert resp.error == "validation_error"
        assert len(resp.detail) == 2

    def test_serialization(self) -> None:
        resp = ErrorResponse(
            error="not_found",
            detail=[ErrorDetail(message="not found")],
        )
        data = resp.model_dump()
        assert data == {
            "error": "not_found",
            "detail": [{"field": None, "message": "not found"}],
        }

    def test_missing_error_raises(self) -> None:
        with pytest.raises(ValidationError):
            ErrorResponse(detail=[ErrorDetail(message="oops")])  # type: ignore[call-arg]

    def test_missing_detail_raises(self) -> None:
        with pytest.raises(ValidationError):
            ErrorResponse(error="bad")  # type: ignore[call-arg]
