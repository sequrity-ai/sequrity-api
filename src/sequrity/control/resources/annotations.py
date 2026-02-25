"""Annotations resource — ``client.control.annotations``.

Provides typed methods for creating, reading, deleting, and batch-creating
session-log annotations via the secure-orchestrator's annotation endpoints.

The annotation endpoints use a separate URL scheme
(``/control/annotations/v1/sessions/...``) and only require Bearer-token
auth — no LLM-specific headers (features, policy, etc.).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..._exceptions import SequrityAPIError, SequrityConnectionError
from .._transport import ControlAsyncTransport, ControlSyncTransport

# ---------------------------------------------------------------------------
# Pydantic models (mirrors the server-side schema)
# ---------------------------------------------------------------------------


class AnnotationSource(str, Enum):
    TAU2_BENCH = "tau2-bench"
    SWE_BENCH = "swe-bench"
    MANUAL = "manual"
    AUTO_PROMPT_CODEX = "auto_prompt_codex"


class AnnotationLabels(BaseModel):
    task_success: bool | None = None
    task_id: str | None = None
    domain: str | None = None
    reward: float | None = Field(default=None, ge=0, le=1)
    error_category: str | None = None


class CreateAnnotationRequest(BaseModel):
    source: AnnotationSource
    labels: AnnotationLabels = Field(default_factory=AnnotationLabels)
    outcome_logs: str | None = None
    metadata: dict[str, Any] | None = None


class Annotation(BaseModel):
    id: str
    timestamp: str
    source: AnnotationSource
    labels: AnnotationLabels
    outcome_logs: str | None = None
    metadata: dict[str, Any] | None = None


class AnnotationFile(BaseModel):
    session_id: str
    annotations: list[Annotation] = Field(default_factory=list)


class BatchAnnotateItem(BaseModel):
    session_id: str
    annotation: CreateAnnotationRequest


class BatchAnnotateRequest(BaseModel):
    items: list[BatchAnnotateItem]


class BatchAnnotateResponse(BaseModel):
    created: list[dict[str, str]]
    errors: list[dict[str, str]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_API_PREFIX = "/control/annotations/v1"


def _annotations_url(base_url: str, path: str) -> str:
    return f"{base_url}{_API_PREFIX}{path}"


def _auth_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Sync resource
# ---------------------------------------------------------------------------


class AnnotationsResource:
    """Session-log annotations — ``client.control.annotations``.

    Example::

        annotation = client.control.annotations.create(
            session_id="004d88f0-...",
            source="tau2-bench",
            labels={"task_success": True, "reward": 1.0},
        )
    """

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    # -- create --------------------------------------------------------------

    def create(
        self,
        session_id: str,
        *,
        source: AnnotationSource | str,
        labels: AnnotationLabels | dict | None = None,
        outcome_logs: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Annotation:
        """Create a single annotation for a session.

        Args:
            session_id: The orchestrator session ID (must have a .log file).
            source: Annotation source identifier.
            labels: Structured labels (task_success, reward, etc.).
            outcome_logs: Free-form description of what happened.
            metadata: Arbitrary key-value metadata.

        Returns:
            The created ``Annotation`` with server-assigned id and timestamp.
        """
        if isinstance(labels, dict):
            labels = AnnotationLabels(**labels)
        body = CreateAnnotationRequest(
            source=AnnotationSource(source),
            labels=labels or AnnotationLabels(),
            outcome_logs=outcome_logs,
            metadata=metadata,
        )
        url = _annotations_url(self._transport._base_url, f"/sessions/{session_id}")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = self._transport._http.post(
                url,
                json=body.model_dump(mode="json"),
                headers=headers,
            )
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return Annotation.model_validate(response.json())

    # -- get -----------------------------------------------------------------

    def get(self, session_id: str) -> AnnotationFile:
        """Get all annotations for a session.

        Args:
            session_id: The orchestrator session ID.

        Returns:
            An ``AnnotationFile`` containing the session's annotations.
        """
        url = _annotations_url(self._transport._base_url, f"/sessions/{session_id}")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = self._transport._http.get(url, headers=headers)
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return AnnotationFile.model_validate(response.json())

    # -- delete --------------------------------------------------------------

    def delete(self, session_id: str, annotation_id: str) -> None:
        """Delete a single annotation by ID.

        Args:
            session_id: The orchestrator session ID.
            annotation_id: The annotation UUID to remove.
        """
        url = _annotations_url(
            self._transport._base_url,
            f"/sessions/{session_id}/{annotation_id}",
        )
        headers = _auth_headers(self._transport._api_key)

        try:
            response = self._transport._http.delete(url, headers=headers)
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

    # -- batch ---------------------------------------------------------------

    def batch_create(
        self,
        items: list[BatchAnnotateItem] | list[dict],
    ) -> BatchAnnotateResponse:
        """Bulk-annotate multiple sessions in one call.

        Args:
            items: List of ``BatchAnnotateItem`` or equivalent dicts, each
                containing ``session_id`` and ``annotation``.

        Returns:
            A ``BatchAnnotateResponse`` with ``created`` and ``errors`` lists.
        """
        parsed = [BatchAnnotateItem(**i) if isinstance(i, dict) else i for i in items]
        body = BatchAnnotateRequest(items=parsed)
        url = _annotations_url(self._transport._base_url, "/sessions/batch")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = self._transport._http.post(
                url,
                json=body.model_dump(mode="json"),
                headers=headers,
            )
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return BatchAnnotateResponse.model_validate(response.json())


# ---------------------------------------------------------------------------
# Async resource
# ---------------------------------------------------------------------------


class AsyncAnnotationsResource:
    """Async variant of :class:`AnnotationsResource`."""

    def __init__(self, transport: ControlAsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        session_id: str,
        *,
        source: AnnotationSource | str,
        labels: AnnotationLabels | dict | None = None,
        outcome_logs: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Annotation:
        """Async variant of :meth:`AnnotationsResource.create`."""
        if isinstance(labels, dict):
            labels = AnnotationLabels(**labels)
        body = CreateAnnotationRequest(
            source=AnnotationSource(source),
            labels=labels or AnnotationLabels(),
            outcome_logs=outcome_logs,
            metadata=metadata,
        )
        url = _annotations_url(self._transport._base_url, f"/sessions/{session_id}")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = await self._transport._http.post(
                url,
                json=body.model_dump(mode="json"),
                headers=headers,
            )
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return Annotation.model_validate(response.json())

    async def get(self, session_id: str) -> AnnotationFile:
        """Async variant of :meth:`AnnotationsResource.get`."""
        url = _annotations_url(self._transport._base_url, f"/sessions/{session_id}")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = await self._transport._http.get(url, headers=headers)
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return AnnotationFile.model_validate(response.json())

    async def delete(self, session_id: str, annotation_id: str) -> None:
        """Async variant of :meth:`AnnotationsResource.delete`."""
        url = _annotations_url(
            self._transport._base_url,
            f"/sessions/{session_id}/{annotation_id}",
        )
        headers = _auth_headers(self._transport._api_key)

        try:
            response = await self._transport._http.delete(url, headers=headers)
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

    async def batch_create(
        self,
        items: list[BatchAnnotateItem] | list[dict],
    ) -> BatchAnnotateResponse:
        """Async variant of :meth:`AnnotationsResource.batch_create`."""
        parsed = [BatchAnnotateItem(**i) if isinstance(i, dict) else i for i in items]
        body = BatchAnnotateRequest(items=parsed)
        url = _annotations_url(self._transport._base_url, "/sessions/batch")
        headers = _auth_headers(self._transport._api_key)

        try:
            response = await self._transport._http.post(
                url,
                json=body.model_dump(mode="json"),
                headers=headers,
            )
        except Exception as exc:
            raise SequrityConnectionError(str(exc)) from exc

        if response.status_code >= 400:
            raise SequrityAPIError.from_response(response)

        return BatchAnnotateResponse.model_validate(response.json())
