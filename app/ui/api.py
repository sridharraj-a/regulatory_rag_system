from __future__ import annotations

from typing import Any

import requests
from requests import Response
from requests.exceptions import ConnectionError, Timeout, RequestException

from constants import (
    QUERY_API_URL,
    UPLOAD_API_URL,
    REQUEST_TIMEOUT,
)


# ------------------------------------------------------------------
# Generic Response Handler
# ------------------------------------------------------------------
def _parse_response(response: Response) -> tuple[dict[str, Any] | None, str | None]:
    """
    Converts a requests.Response into a (result, error) tuple.
    """

    try:
        data = response.json()
    except Exception:
        return None, f"Invalid JSON returned by API.\n\nStatus: {response.status_code}"

    if response.ok:
        return data, None

    # Custom FastAPI ErrorResponse
    if isinstance(data, dict):

        message = data.get("message")

        code = data.get("code")

        if message:
            if code:
                return None, f"{code}\n\n{message}"

            return None, message

    return None, f"HTTP {response.status_code}"


# ------------------------------------------------------------------
# Query API
# ------------------------------------------------------------------
def query_api(question: str) -> tuple[dict[str, Any] | None, str | None]:
    """
    Submit a regulatory question.

    Returns:
        (response_json, error)
    """

    try:

        response = requests.post(
            QUERY_API_URL,
            json={"query": question},
            timeout=REQUEST_TIMEOUT,
        )

        return _parse_response(response)

    except ConnectionError:

        return (
            None,
            "Unable to connect to the Regulatory API.\n\n"
            "Please ensure the FastAPI server is running.",
        )

    except Timeout:

        return (None, "The request timed out while waiting for the API.")

    except RequestException as ex:

        return (None, str(ex))

    except Exception as ex:

        return (None, f"Unexpected error:\n\n{ex}")


# ------------------------------------------------------------------
# Upload PDF
# ------------------------------------------------------------------
def upload_pdf(uploaded_file) -> tuple[dict[str, Any] | None, str | None]:
    """
    Upload a regulatory PDF.

    Returns:
        (response_json, error)
    """

    if uploaded_file is None:

        return (None, "Please choose a PDF first.")

    try:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        }

        response = requests.post(
            UPLOAD_API_URL,
            files=files,
            timeout=300,
        )

        return _parse_response(response)

    except ConnectionError:

        return (None, "Unable to connect to the Regulatory API.")

    except Timeout:

        return (None, "Document upload timed out.")

    except RequestException as ex:

        return (None, str(ex))

    except Exception as ex:

        return (None, f"Unexpected upload error:\n\n{ex}")


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------
def check_api_health() -> bool:
    """
    Used by the sidebar to display API status.
    """

    try:

        response = requests.get(
            "http://127.0.0.1:8000/health",
            timeout=5,
        )

        return response.status_code == 200

    except Exception:

        return False


# ------------------------------------------------------------------
# Version
# ------------------------------------------------------------------
def get_api_version() -> str:
    """
    Returns the API version for the sidebar.
    """

    try:

        response = requests.get(
            "http://127.0.0.1:8000/version",
            timeout=5,
        )

        if response.ok:

            return response.json().get("version", "-")

    except Exception:
        pass

    return "-"
