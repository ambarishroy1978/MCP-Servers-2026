"""Tool implementations for JSON Helper domain."""

import json
from typing import Any, Dict, List, Optional
from framework import (
	ToolExecutionError,
	ValidationError,
	get_app_logger
)
from .models import JSONQueryResult, JSONTransformResult, JSONValidateResult

try:
	from jsonpath_ng import parse as jsonpath_parse
except ImportError:
	jsonpath_parse = None

def _safe_json_loads(data: Any) -> Any:
	if isinstance(data, str):
		return json.loads(data)
	return data

async def json_query_tool(json_data: Any, query: str) -> JSONQueryResult:
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
	logger = get_app_logger()
	logger.info(f"Running dynamic Python query: {query}")
	try:
		# Enforce 1MB (1048576 bytes) max payload
		if isinstance(json_data, str):
			if len(json_data.encode("utf-8")) > 1048576:
				raise ValidationError("Input JSON string exceeds 1MB size limit.")
		else:
			if len(json.dumps(json_data).encode("utf-8")) > 1048576:
				raise ValidationError("Input JSON object exceeds 1MB size limit.")

		data = _safe_json_loads(json_data)

		# Evaluate the query as a Python expression with 'data' in scope
		# Security: Only allow access to 'data' and built-in list comprehensions
		allowed_builtins = {'list': list, 'dict': dict, 'len': len, 'any': any, 'all': all, 'sum': sum, 'min': min, 'max': max, 'str': str, 'int': int, 'float': float, 'bool': bool, 'enumerate': enumerate, 'range': range}
		local_scope = {'data': data}
		try:
			result = eval(query, {"__builtins__": allowed_builtins}, local_scope)
			# Always return a list for consistency
			if not isinstance(result, list):
				result = [result]
			return JSONQueryResult(query=query, result=result, success=True, error=None)
		except Exception as e:
			logger.error(f"Dynamic query failed: {e}")
			return JSONQueryResult(query=query, result=None, success=False, error=str(e))
	except Exception as e:
		logger.error(f"JSON query failed: {e}")
		return JSONQueryResult(query=query, result=None, success=False, error=str(e))

async def json_validate_tool(json_data: Any) -> JSONValidateResult:
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
	logger = get_app_logger()
	logger.info("Validating JSON data")
	errors = []
	# Enforce 1MB (1048576 bytes) max payload
	try:
		if isinstance(json_data, str):
			if len(json_data.encode("utf-8")) > 1048576:
				raise ValidationError("Input JSON string exceeds 1MB size limit.")
		else:
			if len(json.dumps(json_data).encode("utf-8")) > 1048576:
				raise ValidationError("Input JSON object exceeds 1MB size limit.")
		_ = _safe_json_loads(json_data)
		valid = True
	except Exception as e:
		valid = False
		errors.append(str(e))
	return JSONValidateResult(valid=valid, errors=errors)