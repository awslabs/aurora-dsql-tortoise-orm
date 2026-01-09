"""V2 model for add_column migration test - adds description field."""

from tortoise import fields
from tortoise.models import Model


class IncrementalTestModel(Model):
    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=100)
    description = fields.CharField(max_length=200, null=True)

    class Meta:
        table = "incremental_test_model"
