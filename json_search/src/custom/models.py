"""Pydantic models for JSON Helper tools."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class JSONQueryResult(BaseModel):
    """Result of a JSON query operation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "$.store.book[*].author",
                "result": ["Nigel Rees", "Evelyn Waugh"],
                "success": True,
                "error": None,
                "timestamp": "2026-02-17T12:00:00Z"
            }
        }
    )
    query: str = Field(..., description="JSONPath or dot notation query string")
    result: Any = Field(..., description="Result of the query (any JSON-serializable value)")
    success: bool = Field(..., description="Whether the query succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

class JSONTransformResult(BaseModel):
    """Result of a JSON transformation operation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transform": "remove_nulls",
                "result": {"a": 1, "b": 2},
                "success": True,
                "error": None,
                "timestamp": "2026-02-17T12:00:00Z"
            }
        }
    )
    transform: str = Field(..., description="Transformation applied (e.g., remove_nulls, flatten, sort_keys)")
    result: Any = Field(..., description="Transformed JSON object")
    success: bool = Field(..., description="Whether the transformation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

class JSONValidateResult(BaseModel):
    """Result of a JSON validation operation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "errors": [],
                "timestamp": "2026-02-17T12:00:00Z"
            }
        }
    )
    valid: bool = Field(..., description="Whether the JSON is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors, if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")
