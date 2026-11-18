"""URL validation and SSRF protection utilities."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


# Private / reserved CIDR ranges that must be blocked (SSRF protection).
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


class URLValidationError(Exception):
    """Raised when a URL fails validation."""


def validate_url(raw_url: str) -> str:
    """Validate and sanitise a URL, raising URLValidationError on failure.

    Returns the normalised URL string.
    """
    raw_url = str(raw_url).strip()
    if not raw_url:
        raise URLValidationError("URL must not be empty.")

    parsed = urlparse(raw_url)

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise URLValidationError(
            f"Unsupported URL scheme \"{parsed.scheme}\". Only http and https are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must contain a valid hostname.")

    # Block common internal hostnames
    _blocked_hosts = {"localhost", "0.0.0.0", "metadata.google.internal"}
    if hostname.lower() in _blocked_hosts:
        raise URLValidationError(
            f"Access to \"{hostname}\" is not allowed for security reasons."
        )

    # Resolve hostname and check against blocked networks
    try:
        addr_infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise URLValidationError(f"Could not resolve hostname \"{hostname}\".")

    for _family, _type, _proto, _canonname, sockaddr in addr_infos:
        ip = ipaddress.ip_address(sockaddr[0])
        for network in _BLOCKED_NETWORKS:
            if ip in network:
                raise URLValidationError(
                    "Access to private/reserved IP addresses is not allowed (SSRF protection)."
                )

    return raw_url

