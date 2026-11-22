#!/usr/bin/env bash
# Download mcp-publisher for this runner and verify its Sigstore signature,
# as in https://modelcontextprotocol.io/registry/github-actions.md
# Needs cosign on PATH and MCP_PUBLISHER_VERSION set (for example v1.8.12).
set -euo pipefail

: "${MCP_PUBLISHER_VERSION:?set MCP_PUBLISHER_VERSION, e.g. v1.8.12}"
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
arch="$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
archive="mcp-publisher_${os}_${arch}.tar.gz"
base_url="https://github.com/modelcontextprotocol/registry/releases/download/${MCP_PUBLISHER_VERSION}"

curl --fail --location --silent --show-error --output "$archive" "$base_url/$archive"
curl --fail --location --silent --show-error --output "$archive.sigstore.json" "$base_url/$archive.sigstore.json"
cosign verify-blob \
  --bundle "$archive.sigstore.json" \
  --certificate-identity "https://github.com/modelcontextprotocol/registry/.github/workflows/release.yml@refs/tags/${MCP_PUBLISHER_VERSION}" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  "$archive"
tar xzf "$archive" mcp-publisher
rm -f "$archive" "$archive.sigstore.json"
./mcp-publisher --help >/dev/null
