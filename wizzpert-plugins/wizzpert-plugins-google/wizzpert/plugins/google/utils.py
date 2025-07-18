from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

from pydantic import TypeAdapter

from google.genai import types
from wizzpert.agents import llm
from wizzpert.agents.llm import FunctionTool, utils as llm_utils

from .log import logger

__all__ = ["to_chat_ctx", "to_fnc_ctx"]


def to_fnc_ctx(fncs: list[FunctionTool]) -> list[types.FunctionDeclaration]:
    return [_build_gemini_fnc(fnc) for fnc in fncs]


def get_tool_results_for_realtime(
    chat_ctx: llm.ChatContext, *, vertexai: bool = False
) -> types.LiveClientToolResponse | None:
    function_responses: list[types.FunctionResponse] = []
    for msg in chat_ctx.items:
        if msg.type == "function_call_output":
            res = types.FunctionResponse(
                name=msg.name,
                response={"output": msg.output},
            )
            if not vertexai:
                # vertexai does not support id in FunctionResponse
                # see: https://github.com/googleapis/python-genai/blob/85e00bc/google/genai/_live_converters.py#L1435
                res.id = msg.call_id
            function_responses.append(res)
    return (
        types.LiveClientToolResponse(function_responses=function_responses)
        if function_responses
        else None
    )


def to_chat_ctx(
    chat_ctx: llm.ChatContext,
    cache_key: Any,
    ignore_functions: bool = False,
    generate: bool = False,
) -> tuple[list[types.Content], types.Content | None]:
    turns: list[types.Content] = []
    system_instruction: types.Content | None = None
    current_role: str | None = None
    parts: list[types.Part] = []

    for msg in chat_ctx.items:
        if msg.type == "message" and msg.role == "system":
            sys_parts = []
            for content in msg.content:
                if content and isinstance(content, str):
                    sys_parts.append(types.Part(text=content))
            system_instruction = types.Content(parts=sys_parts)
            continue

        if msg.type == "message":
            role = "model" if msg.role == "assistant" else "user"
        elif msg.type == "function_call":
            role = "model"
        elif msg.type == "function_call_output":
            role = "user"

        # if the effective role changed, finalize the previous turn.
        if role != current_role:
            if current_role is not None and parts:
                turns.append(types.Content(role=current_role, parts=parts))
            parts = []
            current_role = role

        if msg.type == "message":
            for content in msg.content:
                if content and isinstance(content, str):
                    parts.append(types.Part(text=content))
                elif content and isinstance(content, dict):
                    parts.append(types.Part(text=json.dumps(content)))
                elif isinstance(content, llm.ImageContent):
                    parts.append(_to_image_part(content, cache_key))
        elif msg.type == "function_call" and not ignore_functions:
            parts.append(
                types.Part(
                    function_call=types.FunctionCall(
                        name=msg.name,
                        args=json.loads(msg.arguments),
                    )
                )
            )
        elif msg.type == "function_call_output" and not ignore_functions:
            parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=msg.name,
                        response={"text": msg.output},
                    )
                )
            )

    if current_role is not None and parts:
        turns.append(types.Content(role=current_role, parts=parts))

    # Gemini requires the last message to end with user's turn before they can generate
    if generate and current_role != "user":
        turns.append(types.Content(role="user", parts=[types.Part(text=".")]))

    return turns, system_instruction


def _to_image_part(image: llm.ImageContent, cache_key: Any) -> types.Part:
    img = llm.utils.serialize_image(image)
    if img.external_url:
        if img.mime_type:
            mime_type = img.mime_type
        else:
            logger.debug("No media type provided for image, defaulting to image/jpeg.")
            mime_type = "image/jpeg"
        return types.Part.from_uri(file_uri=img.external_url, mime_type=mime_type)
    if cache_key not in image._cache:
        image._cache[cache_key] = img.data_bytes
    return types.Part.from_bytes(data=image._cache[cache_key], mime_type=img.mime_type)


def _build_gemini_fnc(function_tool: FunctionTool) -> types.FunctionDeclaration:
    fnc = llm.utils.build_legacy_openai_schema(function_tool, internally_tagged=True)
    json_schema = _GeminiJsonSchema(fnc["parameters"]).simplify()
    return types.FunctionDeclaration(
        name=fnc["name"],
        description=fnc["description"],
        parameters=json_schema,
    )


def to_response_format(response_format: type | dict) -> types.SchemaUnion:
    _, json_schema_type = llm_utils.to_response_format_param(response_format)
    if isinstance(json_schema_type, TypeAdapter):
        schema = json_schema_type.json_schema()
    else:
        schema = json_schema_type.model_json_schema()

    return _GeminiJsonSchema(schema).simplify()


class _GeminiJsonSchema:
    """
    Transforms the JSON Schema from Pydantic to be suitable for Gemini.
    based on pydantic-ai implementation
    https://github.com/pydantic/pydantic-ai/blob/085a9542a7360b7e388ce575323ce189b397d7ad/pydantic_ai_slim/pydantic_ai/models/gemini.py#L809
    """

    # Type mapping from JSON Schema to Gemini Schema
    TYPE_MAPPING: dict[str, types.Type] = {
        "string": types.Type.STRING,
        "number": types.Type.NUMBER,
        "integer": types.Type.INTEGER,
        "boolean": types.Type.BOOLEAN,
        "array": types.Type.ARRAY,
        "object": types.Type.OBJECT,
    }

    def __init__(self, schema: dict[str, Any]):
        self.schema = deepcopy(schema)
        self.defs = self.schema.pop("$defs", {})

    def simplify(self) -> dict[str, Any] | None:
        self._simplify(self.schema, refs_stack=())
        # If the schema is an OBJECT with no properties, return None.
        if self.schema.get("type") == types.Type.OBJECT and not self.schema.get("properties"):
            return None
        return self.schema

    def _simplify(self, schema: dict[str, Any], refs_stack: tuple[str, ...]) -> None:
        schema.pop("title", None)
        schema.pop("default", None)
        schema.pop("additionalProperties", None)
        schema.pop("$schema", None)

        if (const := schema.pop("const", None)) is not None:
            # Gemini doesn't support const, but it does support enum with a single value
            schema["enum"] = [const]

        schema.pop("discriminator", None)
        schema.pop("examples", None)

        if ref := schema.pop("$ref", None):
            key = re.sub(r"^#/\$defs/", "", ref)
            if key in refs_stack:
                raise ValueError("Recursive `$ref`s in JSON Schema are not supported by Gemini")
            refs_stack += (key,)
            schema_def = self.defs[key]
            self._simplify(schema_def, refs_stack)
            schema.update(schema_def)
            return

        # Convert type value to Gemini format
        if "type" in schema and schema["type"] != "null":
            json_type = schema["type"]
            if json_type in self.TYPE_MAPPING:
                schema["type"] = self.TYPE_MAPPING[json_type]
            elif isinstance(json_type, types.Type):
                schema["type"] = json_type
            else:
                raise ValueError(f"Unsupported type in JSON Schema: {json_type}")

        # Map field names that differ between JSON Schema and Gemini
        self._map_field_names(schema)

        # Handle anyOf - map to any_of
        if any_of := schema.pop("anyOf", None):
            if any_of:
                mapped_any_of = []
                has_null = False
                non_null_schema = None

                for item_schema in any_of:
                    self._simplify(item_schema, refs_stack)
                    if item_schema == {"type": "null"}:
                        has_null = True
                    else:
                        non_null_schema = item_schema
                        mapped_any_of.append(item_schema)

                if has_null and len(any_of) == 2 and non_null_schema:
                    schema.update(non_null_schema)
                    schema["nullable"] = True
                else:
                    schema["any_of"] = mapped_any_of

        type_ = schema.get("type")

        if type_ == types.Type.OBJECT:
            self._object(schema, refs_stack)
        elif type_ == types.Type.ARRAY:
            self._array(schema, refs_stack)

    def _map_field_names(self, schema: dict[str, Any]) -> None:
        """Map JSON Schema field names to Gemini Schema field names."""
        mappings = {
            "minLength": "min_length",
            "maxLength": "max_length",
            "minItems": "min_items",
            "maxItems": "max_items",
            "minProperties": "min_properties",
            "maxProperties": "max_properties",
        }

        for json_name, gemini_name in mappings.items():
            if json_name in schema:
                schema[gemini_name] = schema.pop(json_name)

    def _object(self, schema: dict[str, Any], refs_stack: tuple[str, ...]) -> None:
        if properties := schema.get("properties"):
            for value in properties.values():
                self._simplify(value, refs_stack)

    def _array(self, schema: dict[str, Any], refs_stack: tuple[str, ...]) -> None:
        if prefix_items := schema.get("prefixItems"):
            for prefix_item in prefix_items:
                self._simplify(prefix_item, refs_stack)

        if items_schema := schema.get("items"):
            self._simplify(items_schema, refs_stack)
