# SPECTOR Legal Compliance - Implementation Guide

**Priority**: 🔴 CRITICAL  
**Deadline**: End of Week  
**Owner**: Engineering + Legal

This document provides **immediate action items** to address critical legal risks identified in the Legal Risk Assessment.

---

## Critical Mitigations (This Week)

### 1. Disable Extension Cycling (CFAA Risk Mitigation)

**Risk**: Score 10 (ORANGE) - CFAA unauthorized access violations  
**Action**: Disable speculative URL probing immediately

#### Implementation

```python
# src/python/config/feature_flags.py
"""
Feature flags for legal compliance
"""

FEATURE_FLAGS = {
    # CFAA Compliance - Extension cycling DISABLED until legal review
    "extension_cycling_enabled": False,  # DO NOT ENABLE without legal approval
    
    # Only allow explicitly linked files
    "linked_files_only": True,
    
    # Tor usage restrictions
    "tor_for_gov_domains": False,  # Disabled for .gov sites
    "tor_for_media_discovery": False,  # Disabled until legal review
}

def is_feature_enabled(feature_name: str) -> bool:
    """Check if feature is enabled."""
    return FEATURE_FLAGS.get(feature_name, False)
```

```python
# src/python/discovery/media_probe.py
"""
Media discovery with CFAA compliance
"""

from config.feature_flags import is_feature_enabled
import logging

logger = logging.getLogger(__name__)

class MediaProbe:
    """Discover related media files - LEGALLY COMPLIANT VERSION."""
    
    def discover_media(self, document_url: str) -> list:
        """
        Discover media files related to document.
        
        LEGAL COMPLIANCE:
        - Extension cycling DISABLED (CFAA risk)
        - Only follows explicit links
        - Respects robots.txt
        """
        
        # Check if extension cycling is allowed (should be False)
        if is_feature_enabled("extension_cycling_enabled"):
            logger.error("Extension cycling is DISABLED for legal compliance")
            logger.error("Contact legal@SPECTOR.corp to request enabling")
            raise PermissionError("Feature disabled for CFAA compliance")
        
        # Alternative: Extract linked files from HTML/PDF
        return self._extract_linked_files(document_url)
    
    def _extract_linked_files(self, document_url: str) -> list:
        """Extract explicitly linked files (legal method)."""
        # Parse HTML/PDF for <a href>, embedded links
        # Only download files that are explicitly referenced
        pass
```

#### Verification

```bash
# Test that extension cycling is disabled
python -c "from src.python.config.feature_flags import is_feature_enabled; assert not is_feature_enabled('extension_cycling_enabled'), 'FAIL: Extension cycling still enabled!'"
```

---

### 2. Implement robots.txt Compliance (ToS Risk Mitigation)

**Risk**: Score 12 (ORANGE) - Terms of Service violations  
**Action**: Check robots.txt before all HTTP requests

#### Implementation

```python
# src/python/scraping/robots_compliance.py
"""
robots.txt Compliance Module
CRITICAL: CFAA/ToS violation prevention
"""

from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class RobotsCompliance:
    """Enforce robots.txt compliance for all HTTP requests."""
    
    def __init__(self, user_agent: str = "SPECTOR-Research-Bot/1.0"):
        self.user_agent = user_agent
        self._parser_cache = {}
    
    @lru_cache(maxsize=1000)
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched per robots.txt.
        
        Returns:
            True if allowed, False if disallowed
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        # Get or create parser
        if robots_url not in self._parser_cache:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            
            try:
                parser.read()
                self._parser_cache[robots_url] = parser
                logger.info(f"Loaded robots.txt from {robots_url}")
            except Exception as e:
                logger.warning(f"Could not load robots.txt from {robots_url}: {e}")
                # If robots.txt unavailable, assume allowed (permissive)
                return True
        
        parser = self._parser_cache[robots_url]
        allowed = parser.can_fetch(self.user_agent, url)
        
        if not allowed:
            logger.warning(f"robots.txt disallows: {url}")
        
        return allowed
    
    def require_compliance(func):
        """Decorator to enforce robots.txt compliance."""
        def wrapper(self, url: str, *args, **kwargs):
            compliance = RobotsCompliance()
            
            if not compliance.can_fetch(url):
                raise PermissionError(
                    f"robots.txt disallows access to {url}\n"
                    f"User-Agent: {compliance.user_agent}\n"
                    f"Legal compliance requirement - cannot proceed"
                )
            
            return func(self, url, *args, **kwargs)
        
        return wrapper


# Usage Example
class HTTPClient:
    """HTTP client with mandatory robots.txt compliance."""
    
    @RobotsCompliance.require_compliance
    def fetch(self, url: str) -> bytes:
        """Fetch URL with robots.txt compliance check."""
        import requests
        response = requests.get(url)
        return response.content
```

#### Integration into Existing Code

```python
# src/python/scraping/downloader.py

from scraping.robots_compliance import RobotsCompliance

class DocumentDownloader:
    """Download documents with legal compliance."""
    
    def __init__(self):
        self.robots = RobotsCompliance(
            user_agent="SPECTOR-Research-Bot/1.0 (academic research; +https://spector.SPECTOR.corp)"
        )
    
    def download(self, url: str) -> bytes:
        """Download document with compliance checks."""
        
        # MANDATORY: Check robots.txt
        if not self.robots.can_fetch(url):
            logger.error(f"robots.txt blocks {url} - skipping")
            return None
        
        # Proceed with download
        # ... implementation ...
```

#### Verification

```bash
# Test robots.txt compliance
python -m pytest tests/test_robots_compliance.py -v
```

---

### 3. Implement Rate Limiting (ToS Risk Mitigation)

**Risk**: Score 12 (ORANGE) - Excessive automated access  
**Action**: Limit to 1 request/second per domain

#### Implementation

```python
# src/python/scraping/rate_limiter.py
"""
Rate Limiting for Respectful Crawling
Prevents ToS violations from excessive requests
"""

import time
from collections import defaultdict
from threading import Lock
from urllib.parse import urlparse

class RateLimiter:
    """Domain-based rate limiter."""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = defaultdict(float)
        self.lock = Lock()
    
    def wait_if_needed(self, url: str):
        """Wait if necessary to respect rate limit."""
        domain = urlparse(url).netloc
        
        with self.lock:
            last_time = self.last_request_time[domain]
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
                current_time = time.time()
            
            self.last_request_time[domain] = current_time
    
    def __call__(self, func):
        """Decorator for automatic rate limiting."""
        def wrapper(url: str, *args, **kwargs):
            self.wait_if_needed(url)
            return func(url, *args, **kwargs)
        
        return wrapper


# Usage
rate_limiter = RateLimiter(requests_per_second=1.0)

@rate_limiter
def fetch_url(url: str):
    """Fetch URL with automatic rate limiting."""
    import requests
    return requests.get(url)
```

#### Domain-Specific Policies

```python
# config/domain_policies.py
"""
Domain-specific access policies for legal compliance
"""

DOMAIN_POLICIES = {
    # PACER - Federal court records
    "pacer.gov": {
        "allowed": False,  # PROHIBITED - ToS explicitly bans scraping
        "reason": "8th Circuit Rules prohibit automated access",
        "alternative": "Use PACER API with credentials"
    },
    
    # FOIA.gov - Freedom of Information Act
    "foia.gov": {
        "allowed": True,
        "rate_limit": 1.0,  # 1 request/second
        "user_agent": "SPECTOR-Research-Bot/1.0 (academic; +https://spector.SPECTOR.corp)",
        "respect_robots_txt": True
    },
    
    # Justice.gov - DOJ documents
    "justice.gov": {
        "allowed": True,
        "rate_limit": 0.5,  # 1 request/2 seconds (more conservative)
        "user_agent": "SPECTOR-Research-Bot/1.0",
        "respect_robots_txt": True
    },
    
    # Default policy for unknown domains
    "default": {
        "allowed": True,
        "rate_limit": 1.0,
        "require_robots_txt": True,
        "require_manual_approval": True  # Escalate to legal for new domains
    }
}

def get_domain_policy(url: str) -> dict:
    """Get access policy for domain."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    # Check for exact match
    if domain in DOMAIN_POLICIES:
        return DOMAIN_POLICIES[domain]
    
    # Check for subdomain match (e.g., www.justice.gov matches justice.gov)
    for policy_domain, policy in DOMAIN_POLICIES.items():
        if domain.endswith(policy_domain):
            return policy
    
    # Return default policy
    return DOMAIN_POLICIES["default"]
```

---

### 4. Implement GDPR Opt-Out Mechanism (GDPR Risk Mitigation)

**Risk**: Score 12 (ORANGE) - GDPR non-compliance  
**Action**: Build erasure request system

#### Implementation

See detailed implementation in Legal Risk Assessment document, Risk #4, Section 7.

**Quick Start**:

```bash
# Create privacy module
mkdir -p src/python/privacy

# Copy implementation from assessment document
# Files needed:
# - src/python/privacy/opt_out.py (erasure processor)
# - templates/opt_out.html (web form)
# - docs/PRIVACY_POLICY.md (GDPR notice)
```

```python
# src/python/privacy/__init__.py
from .opt_out import OptOutProcessor

__all__ = ['OptOutProcessor']
```

#### Web Form Setup

```python
# src/python/web/privacy_views.py
"""
Django views for GDPR compliance
"""

from django.shortcuts import render
from django.http import JsonResponse
from privacy.opt_out import OptOutProcessor

def opt_out_form(request):
    """Render opt-out request form."""
    return render(request, 'opt_out.html')

def process_opt_out(request):
    """Process GDPR erasure request."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        # Send verification email
        token = send_verification_email(email, name)
        
        return JsonResponse({
            'status': 'verification_sent',
            'message': 'Check your email to confirm the request'
        })

def confirm_opt_out(request, token):
    """Confirm and execute erasure request."""
    processor = OptOutProcessor(neo4j_driver, qdrant_client, mongo_client)
    
    try:
        result = processor.process_erasure_request(name, token)
        
        return JsonResponse({
            'status': 'success',
            'deleted': result
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
```

---

## Verification Checklist

After implementing mitigations, verify compliance:

### Week 1 Checklist

- [ ] Extension cycling disabled (`extension_cycling_enabled = False`)
- [ ] robots.txt compliance implemented
- [ ] Rate limiting active (1 req/sec default)
- [ ] GDPR opt-out form deployed
- [ ] Privacy policy published
- [ ] Domain policy database created
- [ ] Tor disabled for .gov domains
- [ ] All changes tested in development
- [ ] Legal review scheduled (30 days)

### Testing Commands

```bash
# 1. Test feature flags
python -c "from src.python.config.feature_flags import FEATURE_FLAGS; print('Extension cycling:', FEATURE_FLAGS['extension_cycling_enabled'])"
# Expected: Extension cycling: False

# 2. Test robots.txt compliance
python -m pytest tests/test_robots_compliance.py

# 3. Test rate limiting
python tests/manual_test_rate_limiting.py
# Should take 10 seconds to fetch 10 URLs from same domain

# 4. Test GDPR opt-out
curl -X POST http://localhost:8000/privacy/opt-out \
  -d "name=Test User&email=test@example.com"
# Should return verification_sent

# 5. Test domain policies
python -c "from config.domain_policies import get_domain_policy; print(get_domain_policy('https://pacer.gov/doc.pdf'))"
# Expected: {'allowed': False, 'reason': '8th Circuit Rules...'}
```

---

## Deployment Steps

### 1. Development Environment

```bash
# Apply changes
git checkout -b feature/legal-compliance
git add src/python/config/feature_flags.py
git add src/python/scraping/robots_compliance.py
git add src/python/scraping/rate_limiter.py
git add src/python/privacy/opt_out.py
git add config/domain_policies.py
git add docs/PRIVACY_POLICY.md

git commit -m "security: implement critical legal compliance mitigations

- Disable extension cycling (CFAA compliance)
- Add robots.txt compliance (ToS compliance)
- Implement rate limiting (respectful crawling)
- Add GDPR opt-out mechanism (Art. 17 compliance)
- Create domain-specific access policies

Refs: LEGAL_RISK_ASSESSMENT.md
Legal Review: Required before production deployment"

# Run tests
python -m pytest tests/ -v

# Code review
gh pr create --title "Legal Compliance Mitigations" --body "See LEGAL_RISK_ASSESSMENT.md"
```

### 2. Staging Environment

```bash
# Deploy to staging
docker compose -f docker-compose.staging.yml up -d

# Test compliance features
curl https://staging.spector.SPECTOR.corp/privacy/opt-out

# Verify robots.txt is checked
docker logs spector-django | grep "robots.txt"
```

### 3. Production Deployment

**DO NOT DEPLOY TO PRODUCTION** until:
- [ ] Legal counsel review complete
- [ ] CFAA legal opinion obtained
- [ ] All critical mitigations tested
- [ ] Privacy policy reviewed by DPO
- [ ] General Counsel sign-off

---

## Monitoring & Auditing

### Log All Compliance Events

```python
# src/python/monitoring/compliance_logger.py
"""
Compliance event logging for legal audit trail
"""

import logging
from pythonjsonlogger import jsonlogger

compliance_logger = logging.getLogger('spector.compliance')

def log_compliance_event(event_type: str, details: dict):
    """Log compliance event to audit trail."""
    compliance_logger.info(
        f"Compliance event: {event_type}",
        extra={
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            **details
        }
    )

# Usage
log_compliance_event('robots_txt_block', {
    'url': 'https://example.com/page',
    'user_agent': 'SPECTOR-Research-Bot',
    'reason': 'Disallowed in robots.txt'
})

log_compliance_event('gdpr_erasure', {
    'data_subject_hash': hashlib.sha256(name.encode()).hexdigest(),
    'systems_updated': ['qdrant', 'neo4j', 'mongodb'],
    'requester_verified': True
})
```

### Compliance Metrics

```python
# src/python/monitoring/compliance_metrics.py
"""
Prometheus metrics for compliance monitoring
"""

from prometheus_client import Counter, Histogram

robots_txt_blocks = Counter(
    'spector_robots_txt_blocks_total',
    'URLs blocked by robots.txt',
    ['domain']
)

gdpr_requests = Counter(
    'spector_gdpr_requests_total',
    'GDPR requests processed',
    ['request_type', 'status']
)

rate_limit_delays = Histogram(
    'spector_rate_limit_delay_seconds',
    'Time spent waiting for rate limits',
    ['domain']
)
```

### Grafana Dashboard

Create compliance dashboard with:
- robots.txt blocks per domain
- GDPR requests per day
- Rate limiting delays
- Blocked domains (PACER, etc.)
- Feature flag status (extension_cycling should be OFF)

---

## Emergency Procedures

### If Cease-and-Desist Received

1. **Immediate Actions**:
   ```bash
   # Stop all scraping immediately
   docker compose down
   
   # Disable web access
   # Block domain in firewall
   ```

2. **Notify**:
   - General Counsel: legal@SPECTOR.corp
   - Engineering Lead: engineering@SPECTOR.corp
   - CEO: executive@SPECTOR.corp

3. **Preserve Evidence**:
   - Save all logs
   - Screenshot relevant code
   - Export compliance audit trail

### If GDPR Complaint Filed

1. **30-Day Response Deadline** (GDPR Art. 12(3))
2. **Immediate Actions**:
   - Process any pending erasure requests
   - Audit compliance with GDPR
   - Prepare response documentation

3. **Notify DPO** (if designated)

---

## Legal Contacts

**For Questions About This Implementation**:
- Legal Lead: legal@SPECTOR.corp
- Compliance Officer: compliance@SPECTOR.corp

**For Outside Counsel Engagement**:
- General Counsel approval required
- Budget: $5,000-$10,000 for CFAA opinion

---

## Timeline Summary

| Task | Deadline | Owner | Status |
|------|----------|-------|--------|
| Disable extension cycling | End of Week | Engineering | ⏳ In Progress |
| Implement robots.txt | End of Week | Engineering | ⏳ In Progress |
| Add rate limiting | End of Week | Engineering | ⏳ In Progress |
| GDPR opt-out mechanism | End of Week | Eng + Legal | ⏳ In Progress |
| Privacy policy | End of Week | Legal | ⏳ In Progress |
| Legal counsel engagement | Within 30 days | General Counsel | 📋 Pending |
| CFAA legal opinion | Within 60 days | Outside Counsel | 📋 Pending |
| Production deployment | After legal review | Engineering | 🔒 Blocked |

---

**Document Status**: ACTIVE IMPLEMENTATION GUIDE  
**Last Updated**: 2026-02-19  
**Next Review**: Weekly until completion

**Legal Review Required**: Yes - do not deploy to production without legal sign-off
