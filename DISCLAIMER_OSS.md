# SPECTOR Legal Notice and Usage Disclaimer

SPECTOR is a research and analysis toolkit designed to index, search, and explore **publicly available** documents and datasets. It is provided for academic, journalistic, and personal research purposes only. It is **not** intended or advertised for use in circumventing legal restrictions, accessing non-public systems, or violating any applicable terms of service.

## Scope of Data

- SPECTOR is designed to operate only on:
  - Documents and datasets that are publicly released by official sources (e.g., DOJ online libraries, court PACER alternatives where permitted, government FOIA libraries).
  - Publicly accessible open-source repositories (e.g., GitHub projects such as epstein-files.org, epstein-docs.github.io, Erik Veland/epstein-archive, Librarius).
- SPECTOR does **not** include or require:
  - Access to authentication-gated or paywalled services in violation of their terms of use.
  - Access to sealed, expunged, or otherwise non-public records.
  - Bypassing technical protection measures on any system.

You are solely responsible for verifying that any data you process with SPECTOR is lawfully accessible in your jurisdiction.

## No Unauthorized Access (CFAA / "Hacking" Clarification)

SPECTOR does **not** perform, and is not intended to be configured to perform:

- Brute-forcing of credentials, session tokens, or API keys.
- Exploitation of vulnerabilities or bypass of access controls.
- Access to non-public network services or internal endpoints.

SPECTOR's default configuration is restricted to fetching documents from URLs that:

1. Are publicly available without login; and  
2. Are compatible with the site's robots.txt and terms of service.

If you modify SPECTOR to target endpoints that are not intended for public access, you may violate the U.S. Computer Fraud and Abuse Act (18 U.S.C. § 1030) or analogous laws. The project authors and contributors do **not** endorse, authorize, or accept responsibility for any such use.

## Terms of Service & robots.txt

Many websites (including government and court systems) publish:

- **Terms of Service / Terms of Use**, and  
- **robots.txt** files specifying automated access rules.

By default, SPECTOR:

- Honors robots.txt for each target domain.
- Implements rate limiting suitable for polite crawling.
- Does not attempt to access disallowed paths.

You are responsible for reviewing and complying with the terms of any site you target. If a site prohibits automated scraping, **do not** point SPECTOR at it.

## PDF Redaction and Security Research

SPECTOR includes optional modules for:

- Extracting embedded text from PDFs (including OCR text layers).
- Analyzing the effectiveness of redaction methods on publicly released documents.

These capabilities are intended to:

- Evaluate the security of redaction techniques on already public documents.
- Support academic/security research on document redaction best practices.

They are **not** intended for, and must not be used to:

- Defeat court sealing orders or protective orders.
- Access non-public information where disclosure is prohibited by law.

Any such use may be illegal and could expose the user to civil or criminal liability. The maintainers do not encourage or condone using SPECTOR against sealed, non-released, or illegally obtained documents.

## Privacy and Personal Data

SPECTOR may process personal data contained in public-record documents (e.g., names, addresses, or other personally identifiable information contained in government releases).

- The maintainers do **not** collect or operate any hosted service or centralized index of user data.
- All processing occurs on infrastructure controlled by the user (local machine or user-controlled cloud project).
- Any obligations under GDPR, CCPA, or other privacy laws attach to the **operator** of an instance, not the upstream project authors.

If you deploy SPECTOR in the EU/EEA, UK, or other privacy-regulated jurisdictions, you are responsible for:

- Determining your role (controller vs. processor).
- Establishing a legal basis for processing.
- Implementing any required data subject rights workflow (access, erasure, etc.).

## No Legal Advice

Nothing in this repository, its documentation, or disclaimers constitutes legal advice.  

Use of SPECTOR may have legal implications depending on your jurisdiction and specific use case. You should consult with qualified legal counsel if you have questions about:

- Computer crime laws (e.g., CFAA).
- Copyright and fair use.
- Data protection and privacy.
- Terms-of-service and contract compliance.

## Third-Party References and Sources

SPECTOR may refer to, or interoperate with, external public resources and open-source projects, including but not limited to:

- Public document archives such as epstein-files.org and epstein-docs.github.io.
- Independent analysis projects (e.g., Librarius, ErikVeland/epstein-archive).
- Vector databases, knowledge graph tools, and AI model providers.

These third-party services and datasets are not controlled by the SPECTOR maintainers. Their availability, accuracy, and legal status may change over time. Inclusion of references does **not** constitute endorsement of any third-party's views, methods, or curation practices.

## Tor and Network Anonymity

SPECTOR can optionally be configured to route traffic through Tor or other anonymity networks.  

If you enable these options:

- Do **not** use Tor to access services that prohibit Tor or anonymized connections in their terms of use.
- Do **not** use anonymity features to conceal activities that would otherwise violate law or contract.

You remain responsible for all network traffic originating from your deployment.

## Acceptance

By installing, running, or contributing to SPECTOR, you acknowledge that:

- The software is provided "AS IS", without warranty of any kind.
- You are solely responsible for ensuring that your use complies with all applicable laws and terms.
- The maintainers and contributors are not liable for your use or misuse of the software.

---

**SPDX-License-Identifier: MIT**  
**Copyright © 2024-2026 SPECTOR Contributors**
