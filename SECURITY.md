# Security Policy

## Scope

This repository contains **Hermes AI agent code and configuration** for the
`jolarca-dev` marketplace fleet. It does NOT contain live API credentials,
cryptographic key material, or production secrets.

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, report it through
the [jolarca-dev security policy](https://github.com/jolarca-dev/.github/blob/main/SECURITY.md).

## What to Include

- Description of the vulnerability and its potential impact
- Affected file(s) and the specific component concerned
- Steps to reproduce or demonstrate the issue
- Suggested remediation (if any)

## Response Timeline

| Severity | Response | Remediation |
| --- | --- | --- |
| Critical | Immediate | Same-day patch |
| High | Within 24 hours | Within 72 hours |
| Medium | Within 72 hours | Next scheduled review |
| Low | Next business day | Next scheduled review |

## Do NOT

- Commit credentials, tokens, API keys, or cryptographic key material
- Commit Terraform state files (*.tfstate, *.tfstate.*)
- Reference mission-platform resources (ADR-0004 R4)
