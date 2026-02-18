"""JSON Helper tool registrations."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from framework import register_tool

from .tools import json_query_tool, json_validate_tool
from .models import JSONQueryResult, JSONValidateResult

# Parameter models
class JSONQueryParams(BaseModel):
	json_data: Any = Field(..., description="JSON object or string to query")
	query: str = Field(..., description="JSONPath or dot notation query string")

class JSONValidateParams(BaseModel):
	json_data: Any = Field(..., description="JSON object or string to validate")

# Tool registrations
@register_tool("json_query")
async def json_query_tool_wrapper(params: JSONQueryParams) -> Dict[str, Any]:
	"""
	Query a JSON object using a dynamic Python expression.

	Example input:
		{
		"json_data": {
			"orders": [
			{"order_id": "7f6e1234-e89b-12d3-a456-426614174000", "items": []}
			]
		},
		"query": "[order[\"order_id\"] for order in data[\"orders\"] for item in order[\"items\"] if item[\"item_id\"] == 203 and item[\"item_type_id\"] == 9]"
		}
	
		Returns:
		{
			"query": "[order[\"order_id\"] for order in data[\"orders\"] for item in order[\"items\"] if item[\"item_id\"] == 203 and item[\"item_type_id\"] == 9]",
			"result": [
				"a1b2c3d4-e5f6-4789-abcd-1234567890ab"
			],
			"success": true,
			"error": null,
			"timestamp": "2026-02-17T13:39:08.657624"
		}
	
	"""
	result = await json_query_tool(params.json_data, params.query)
	return result.model_dump()

@register_tool("json_validate")
async def json_validate_tool_wrapper(params: JSONValidateParams) -> Dict[str, Any]:
	"""
	Validate if the input is valid JSON.

	Example input:
		{
			"json_data": {
			"orders": [
				{"order_id": "7f6e1234-e89b-12d3-a456-426614174000", "items": []}
			]
			}
		}

		Returns:
		{
			"valid": true,
			"errors": []
		}

	"""
	result = await json_validate_tool(params.json_data)
	return result.model_dump()
