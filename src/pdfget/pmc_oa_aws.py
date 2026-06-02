"""
PMC OA AWS 下载器

通过公开的 S3 桶 pmc-oa-opendata 访问并下载 PMC OA PDF。
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import cast

import requests

from .logger import get_logger


class PMCOAAWSService:
    """PMC OA AWS 下载器（匿名访问 S3）"""

    def __init__(self, output_dir: str, session: requests.Session):
        self.logger = get_logger(__name__)
        self.output_dir = Path(output_dir)
        self.session = session
        self.bucket = "pmc-oa-opendata"
        self.base_url = f"https://{self.bucket}.s3.amazonaws.com"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _list_versions(self, pmcid: str) -> list[str]:
        """List all version prefixes for a PMCID using S3 ListObjectsV2."""
        prefix = f"{pmcid}."
        url = f"{self.base_url}/?list-type=2&prefix={prefix}&delimiter=/"

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                self.logger.error(
                    f"AWS list-objects returned {response.status_code} for {pmcid}"
                )
                return []

            root = ET.fromstring(response.text)
            prefixes = [
                elem.text
                for elem in root.findall(".//{*}CommonPrefixes/{*}Prefix")
                if elem.text
            ]
            return prefixes
        except requests.RequestException as exc:
            self.logger.error(f"AWS list-objects request failed for {pmcid}: {exc}")
            return []
        except ET.ParseError as exc:
            self.logger.error(f"AWS list-objects XML parse failed for {pmcid}: {exc}")
            return []

    def _select_latest_version(self, pmcid: str, prefixes: list[str]) -> str | None:
        """Pick the latest version prefix like PMC12345.2/"""
        versions: list[tuple[int, str]] = []
        for prefix in prefixes:
            if not prefix.startswith(f"{pmcid}."):
                continue
            if not prefix.endswith("/"):
                continue
            version_str = prefix[len(pmcid) + 1 : -1]
            if not version_str.isdigit():
                continue
            versions.append((int(version_str), prefix[:-1]))

        if not versions:
            return None

        versions.sort(key=lambda item: item[0])
        return versions[-1][1]

    def _get_metadata(self, version_id: str) -> dict[str, object] | None:
        """Fetch metadata JSON for a specific version id like PMC12345.1."""
        url = f"{self.base_url}/metadata/{version_id}.json"
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                self.logger.error(
                    f"AWS metadata returned {response.status_code} for {version_id}"
                )
                return None
            return cast(dict[str, object], response.json())
        except requests.RequestException as exc:
            self.logger.error(f"AWS metadata request failed for {version_id}: {exc}")
            return None
        except json.JSONDecodeError as exc:
            self.logger.error(f"AWS metadata JSON parse failed for {version_id}: {exc}")
            return None

    def _s3_to_https(self, s3_url: str) -> str:
        """Convert s3://pmc-oa-opendata/... to https://pmc-oa-opendata.s3.amazonaws.com/..."""
        prefix = f"s3://{self.bucket}/"
        if s3_url.startswith(prefix):
            return s3_url.replace(prefix, f"{self.base_url}/", 1)
        return s3_url

    def _download_pdf(self, url: str, output_path: Path) -> bool:
        """Download a PDF to the target path."""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            return True
        except requests.RequestException as exc:
            self.logger.error(f"AWS PDF download failed: {exc}")
            return False
        except OSError as exc:
            self.logger.error(f"AWS PDF save failed: {exc}")
            return False

    def download_pdf(self, pmcid: str, output_path: Path) -> dict[str, str | bool | int]:
        """Download PMC OA PDF from AWS for a given PMCID."""
        if not pmcid.startswith("PMC"):
            pmcid = f"PMC{pmcid}"

        prefixes = self._list_versions(pmcid)
        version_id = self._select_latest_version(pmcid, prefixes)
        if not version_id:
            return {"success": False, "error": "No versions found on AWS"}

        metadata = self._get_metadata(version_id)
        pdf_url = None
        if metadata and metadata.get("pdf_url"):
            pdf_url = self._s3_to_https(str(metadata["pdf_url"]))
        else:
            pdf_url = f"{self.base_url}/{version_id}/{version_id}.pdf"

        self.logger.info(f"AWS 下载 PDF: {version_id}")
        if not self._download_pdf(pdf_url, output_path):
            return {
                "success": False,
                "error": "AWS PDF download failed",
                "source_url": pdf_url,
                "version": version_id,
            }

        size = output_path.stat().st_size if output_path.exists() else 0
        return {
            "success": True,
            "path": str(output_path),
            "source_url": pdf_url,
            "content_length": size,
            "version": version_id,
        }
