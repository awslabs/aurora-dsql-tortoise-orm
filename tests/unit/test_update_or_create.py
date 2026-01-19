# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tortoise import fields

from aurora_dsql_tortoise import DSQLModel


class UpdateOrCreateModel(DSQLModel):
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    name = fields.CharField(max_length=100)

    class Meta:
        table = "update_or_create_model"


@pytest.fixture
def mock_env():
    """Patches the environment to avoid real DB connections."""
    mock_db = MagicMock(connection_name="default")
    mock_queryset = MagicMock()
    with patch.object(UpdateOrCreateModel, "filter", return_value=mock_queryset):
        yield mock_db, mock_queryset


@pytest.mark.asyncio
async def test_creates_new_row(mock_env):
    """When row doesn't exist, should create new row."""
    mock_db, mock_queryset = mock_env
    instance = UpdateOrCreateModel(name="new")
    mock_queryset.using_db.return_value.get_or_none = AsyncMock(return_value=None)

    with patch.object(
        UpdateOrCreateModel, "_create_or_get", return_value=(instance, True)
    ) as mock_create:
        result, created = await UpdateOrCreateModel.update_or_create(
            defaults={"name": "new"}, using_db=mock_db, id=instance.id
        )

    assert result.name == "new"
    assert created is True
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_applies_defaults_when_row_exists(mock_env):
    """When row exists, defaults should be applied."""
    mock_db, mock_queryset = mock_env
    instance = UpdateOrCreateModel(name="original")
    mock_queryset.using_db.return_value.get_or_none = AsyncMock(return_value=instance)

    with patch.object(instance, "save", new_callable=AsyncMock) as mock_save:
        result, created = await UpdateOrCreateModel.update_or_create(
            defaults={"name": "updated"}, using_db=mock_db, id=instance.id
        )

    assert result.name == "updated"
    assert created is False
    mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_empty_defaults(mock_env):
    """When defaults is empty, should still save."""
    mock_db, mock_queryset = mock_env
    instance = UpdateOrCreateModel(name="original")
    mock_queryset.using_db.return_value.get_or_none = AsyncMock(return_value=instance)

    with patch.object(instance, "save", new_callable=AsyncMock) as mock_save:
        result, created = await UpdateOrCreateModel.update_or_create(
            using_db=mock_db, id=instance.id
        )

    assert result.name == "original"
    assert created is False
    mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_applies_defaults_when_row_created_after_existence_check(mock_env):
    """When another transaction creates the row after get_or_none returns None,
    defaults must still be applied."""
    mock_db, mock_queryset = mock_env
    instance = UpdateOrCreateModel(name="original")
    mock_queryset.using_db.return_value.get_or_none = AsyncMock(return_value=None)

    with (
        patch.object(UpdateOrCreateModel, "_create_or_get", return_value=(instance, False)),
        patch.object(instance, "save", new_callable=AsyncMock) as mock_save,
    ):
        result, created = await UpdateOrCreateModel.update_or_create(
            defaults={"name": "updated"}, using_db=mock_db, id=instance.id
        )

    assert result.name == "updated"
    assert created is False
    mock_save.assert_called_once()
