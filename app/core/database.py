from boto3 import resource, resources
from typing import Dict, Any, Optional
from fastapi.concurrency import run_in_threadpool

from core.config import Config


class DBClient:
    _region = Config.AWS_DEFAULT_REGION
    _dynamodb: resources.base.ServiceResource = None

    @classmethod
    def _get_table(cls, table_name: str):
        if cls._dynamodb is None:
            cls._dynamodb = resource("dynamodb", region_name=cls._region)
        return cls._dynamodb.Table(table_name)

    @classmethod
    async def put_item(cls, table_name: str, item: Dict[str, Any]) -> None:
        table = cls._get_table(table_name)
        await run_in_threadpool(table.put_item, Item=item)

    @classmethod
    async def get_item(
        cls, table_name: str, key: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        table = cls._get_table(table_name)
        response = await run_in_threadpool(table.get_item, Key=key)
        return response.get("Item")

    @classmethod
    async def query(
        cls,
        table_name: str,
        index_name: Optional[str],
        key_condition: str,
        values: Dict[str, Any],
    ) -> list[Dict[str, Any]]:
        table = cls._get_table(table_name)

        kwargs = {
            "KeyConditionExpression": key_condition,
            "ExpressionAttributeValues": values,
        }

        if index_name:
            kwargs["IndexName"] = index_name

        response = await run_in_threadpool(table.query, **kwargs)
        return response.get("Items", [])

    @classmethod
    async def update_item(
        cls,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        table = cls._get_table(table_name)
        response = await run_in_threadpool(
            table.update_item,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")
