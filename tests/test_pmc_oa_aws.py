#!/usr/bin/env python3
"""Unit tests for PMC OA AWS downloader."""

from pathlib import Path
from unittest.mock import Mock

import requests

from src.pdfget.pmc_oa_aws import PMCOAAWSService


def _make_response(status_code: int = 200, text: str | None = None, json_data=None):
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.text = text or ""
    response.json.return_value = json_data
    response.iter_content.return_value = [b"pdf-data"]
    response.raise_for_status.return_value = None
    return response


def test_select_latest_version():
    session = Mock(spec=requests.Session)
    service = PMCOAAWSService("/tmp", session)

    prefixes = ["PMC13115980.1/", "PMC13115980.3/", "PMC13115980.2/"]
    latest = service._select_latest_version("PMC13115980", prefixes)

    assert latest == "PMC13115980.3"


def test_select_latest_version_alt():
    session = Mock(spec=requests.Session)
    service = PMCOAAWSService("/tmp", session)

    prefixes = ["PMC8696154.1/", "PMC8696154.2/"]
    latest = service._select_latest_version("PMC8696154", prefixes)

    assert latest == "PMC8696154.2"


def test_download_pdf_uses_metadata(tmp_path: Path):
    session = Mock(spec=requests.Session)
    service = PMCOAAWSService(str(tmp_path), session)

    list_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CommonPrefixes><Prefix>PMC10160550.1/</Prefix></CommonPrefixes>
    <CommonPrefixes><Prefix>PMC10160550.2/</Prefix></CommonPrefixes>
</ListBucketResult>"""
    metadata = {
                "pdf_url": "s3://pmc-oa-opendata/PMC10160550.2/PMC10160550.2.pdf?md5=abc"
    }

    list_response = _make_response(text=list_xml)
    metadata_response = _make_response(json_data=metadata)
    pdf_response = _make_response()

    def _side_effect(url, *args, **kwargs):
        if "list-type=2" in url:
            return list_response
        if "/metadata/" in url:
            return metadata_response
        return pdf_response

    session.get.side_effect = _side_effect

    output_path = tmp_path / "PMC10160550.pdf"
    result = service.download_pdf("PMC10160550", output_path)

    assert result["success"] is True
    assert output_path.exists()
    assert output_path.read_bytes() == b"pdf-data"
