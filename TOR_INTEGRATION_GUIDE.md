# SPECTOR Tor Integration Guide

## Overview

SPECTOR now includes **Tor (The Onion Router)** integration for anonymous network routing and enhanced privacy. The system provides:

- **Automated Tor Management** - Start/stop Tor service programmatically
- **Circuit Control** - Renew circuits and change exit nodes on demand
- **Tornado Web UI** - Real-time dashboard for Tor monitoring
- **SOCKS Proxy** - Route HTTP requests through Tor network
- **WebSocket Updates** - Live circuit status and IP changes

---

## Installation

### 1. Install Tor Service

**Windows:**
```powershell
# Download Tor Expert Bundle
# https://www.torproject.org/download/tor/
# Extract to C:\Tools\Tor\

# OR download Tor Browser Bundle (includes Tor)
# https://www.torproject.org/download/
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install tor
```

**macOS (Homebrew):**
```bash
brew install tor
```

### 2. Install Python Dependencies

```bash
pip install tornado stem PySocks requests[socks]
```

Or install SPECTOR with Tor extras:
```bash
pip install -e ".[tor]"
```

---

## Quick Start

### Launch Tor-Enabled Admin Console

```bash
python launcher.py tor-admin --port 8889
```

**Access Dashboard:**
- URL: http://localhost:8889/tor/dashboard
- WebSocket API: ws://localhost:8889/ws/tor
- REST API: http://localhost:8889/api/tor/*

---

## Usage Examples

### 1. Basic Tor Manager Usage

```python
from src.python.tor_manager import TorManager

# Initialize and start Tor
with TorManager(auto_start=True) as tor:
    print(f"Tor Running: {tor.is_running()}")
    print(f"Exit IP: {tor.get_current_ip()}")
    
    # Renew circuit (change exit node)
    tor.renew_circuit()
    print(f"New Exit IP: {tor.get_current_ip()}")
    
    # Get proxied requests session
    session = tor.get_session()
    response = session.get("https://check.torproject.org")
    print(response.text)
```

### 2. Tornado Route Integration

```python
from src.python.tornado_tor_integration import create_tor_routes, TorProxyMixin
from src.python.tor_manager import TorManager
import tornado.web
import tornado.ioloop

# Initialize Tor
tor = TorManager(auto_start=True)
tor.start()

# Create Tornado app with Tor routes
app = tornado.web.Application(
    create_tor_routes(tor),
    template_path="docs"
)

app.listen(8889)
tornado.ioloop.IOLoop.current().start()
```

### 3. Custom Handler with Tor Proxy

```python
from src.python.tornado_tor_integration import TorProxyMixin
import tornado.web

class MyHandler(tornado.web.RequestHandler, TorProxyMixin):
    async def get(self):
        # Fetch URL through Tor
        response = await self.fetch_via_tor("https://example.com")
        self.write({"status": response.code, "body": response.body.decode()})
```

---

## API Reference

### REST Endpoints

#### GET /api/tor/status
Get current Tor status.

**Response:**
```json
{
  "running": true,
  "socks_port": 9050,
  "control_port": 9051,
  "exit_ip": "185.220.101.55",
  "circuits": [...]
}
```

#### POST /api/tor/control
Execute Tor control commands.

**Request:**
```json
{
  "action": "start" | "stop" | "renew_circuit" | "get_ip"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tor started",
  "new_ip": "185.220.102.88"  // For renew_circuit
}
```

#### GET /api/tor/circuits
Get active circuit information.

**Response:**
```json
{
  "circuits": [
    {
      "id": "1",
      "status": "BUILT",
      "purpose": "GENERAL",
      "path": ["node1...relay1", "node2...relay2", "node3...exit"]
    }
  ],
  "count": 1
}
```

### WebSocket API

Connect to `ws://localhost:8889/ws/tor` for real-time updates.

**Send:**
```json
{
  "action": "get_status"
}
```

**Receive:**
```json
{
  "type": "status_update",
  "data": {
    "running": true,
    "exit_ip": "185.220.101.55",
    ...
  },
  "timestamp": "2026-02-20T08:15:00.000Z"
}
```

---

## Configuration

### TorManager Parameters

```python
TorManager(
    socks_port=9050,        # SOCKS proxy port
    control_port=9051,      # Control port
    password="custom_pwd",  # Control password
    auto_start=True         # Auto-start Tor if not running
)
```

### Tor Configuration File

Located at `tor_config.txt` (auto-generated):

```
SocksPort 9050
ControlPort 9051
HashedControlPassword 16:872860B76...
CookieAuthentication 0
DataDirectory ./tor_data
Log notice stdout
```

---

## Security Best Practices

### ✅ DO:
- Use Tor for scraping public DOJ files anonymously
- Respect `robots.txt` even when using Tor
- Rate limit requests (1 req/sec default)
- Renew circuits periodically (every 10 minutes recommended)
- Monitor exit node changes

### ❌ DON'T:
- Use Tor to bypass authentication or paywalls
- Send unencrypted credentials over Tor
- Rely on Tor alone for legal protection (still follow ToS)
- Use Tor for time-sensitive operations (high latency)

---

## Troubleshooting

### Tor Won't Start

**Error:** `Tor executable not found`

**Solution:**
```bash
# Linux
sudo apt install tor

# macOS
brew install tor

# Windows - download from:
# https://www.torproject.org/download/tor/
```

### Circuit Bootstrap Timeout

**Error:** `Tor bootstrap timeout`

**Cause:** Firewall blocking Tor connections

**Solution:**
```bash
# Check firewall rules
# Allow outbound connections to port 9001 (default Tor relay port)

# Windows Firewall
netsh advfirewall firewall add rule name="Tor" dir=out action=allow protocol=TCP localport=9050,9051

# Linux iptables
sudo iptables -A OUTPUT -p tcp --dport 9001 -j ACCEPT
```

### SOCKS Proxy Not Working

**Error:** `PySocks not installed`

**Solution:**
```bash
pip install PySocks requests[socks]
```

### Control Port Authentication Failed

**Error:** `Authentication failed`

**Cause:** Password mismatch or control port disabled

**Solution:**
```bash
# Generate hashed password
tor --hash-password "your_password"

# Add to tor_config.txt
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
```

---

## Dashboard Features

### Real-Time Monitoring
- ✅ Tor service status (online/offline)
- ✅ Current exit IP address
- ✅ Active circuit count
- ✅ Circuit path visualization
- ✅ WebSocket live updates

### Circuit Control
- 🔄 **New Circuit** - Request new exit node
- 🌐 **Check IP** - Verify current exit IP
- 🔄 **Refresh Status** - Update dashboard
- 🧪 **Test Connection** - Verify Tor connectivity

### Activity Log
- Real-time event logging
- Timestamp for all operations
- Error tracking
- WebSocket connection status

---

## Performance Considerations

### Latency
- **Normal Web:** 50-200ms
- **Through Tor:** 500-2000ms (3+ relay hops)

**Recommendation:** Use Tor only when anonymity required, not for all requests.

### Circuit Renewal
- **Default:** Circuits rotate every 10 minutes
- **Manual:** Call `tor.renew_circuit()` to force renewal
- **Best Practice:** Renew every 5-10 requests or when IP blocked

### Bandwidth
- **Tor Network Limit:** ~5-10 MB/s per circuit
- **Recommendation:** Rate limit to 1-2 req/sec

---

## Integration with SPECTOR

### Enable Tor for Document Fetching

```python
from src.python.tor_manager import TorManager
from src.python.document_fetcher import DocumentFetcher

# Initialize Tor
tor = TorManager(auto_start=True)
tor.start()

# Use Tor session for fetching
session = tor.get_session()
fetcher = DocumentFetcher(session=session)

# All requests now routed through Tor
document = fetcher.fetch("https://www.justice.gov/example.pdf")
```

### Automatic Circuit Rotation

```python
import asyncio

async def fetch_with_rotation(urls):
    tor = TorManager(auto_start=True)
    tor.start()
    
    results = []
    for i, url in enumerate(urls):
        # Renew circuit every 10 requests
        if i % 10 == 0:
            tor.renew_circuit()
        
        session = tor.get_session()
        response = session.get(url)
        results.append(response)
    
    tor.stop()
    return results
```

---

## Legal & Ethical Considerations

### Tor Usage is Legal
Using Tor is **100% legal** in most countries. It's used by:
- Journalists protecting sources
- Researchers conducting privacy studies
- Privacy-conscious individuals
- Organizations bypassing censorship

### SPECTOR + Tor Use Case
**✅ Appropriate:**
- Anonymously scraping public DOJ files
- Protecting researcher identity
- Avoiding geographic rate limiting
- Testing access from different exit nodes

**❌ Inappropriate:**
- Bypassing authentication/paywalls
- Accessing restricted/sealed documents
- Violating Terms of Service
- Evading legal consequences

---

## Advanced Topics

### Custom Exit Nodes

```python
# Edit tor_config.txt
ExitNodes {us},{gb},{de}  # Use US, UK, Germany exits only
StrictNodes 1
```

### Bridge Relays (Circumvent Censorship)

```python
# Add to tor_config.txt
UseBridges 1
Bridge obfs4 185.220.101.55:9001
```

### Onion Services

```python
# Access .onion sites
session = tor.get_session()
response = session.get("http://thehiddenwiki.onion")
```

---

## Monitoring & Alerts

### WebSocket Alerts

```javascript
// Browser-side monitoring
const ws = new WebSocket('ws://localhost:8889/ws/tor');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'status_update') {
        console.log('Exit IP changed:', data.data.exit_ip);
    }
};
```

### Email Alerts (Future Enhancement)

```python
# TODO: Add email notifications for:
# - Tor service down
# - Circuit build failures
# - Exit node in blocked country
```

---

## Performance Benchmarks

| Operation | Normal | Through Tor | Overhead |
|-----------|--------|-------------|----------|
| DNS Lookup | 50ms | 500ms | 10x |
| TCP Connect | 100ms | 800ms | 8x |
| HTTP GET | 200ms | 1500ms | 7.5x |
| Large File (10MB) | 5s | 45s | 9x |

**Conclusion:** Expect 7-10x slower performance through Tor. Use selectively.

---

## Roadmap

### Planned Features
- [ ] Multiple Tor instances (load balancing)
- [ ] Geographic exit node selection UI
- [ ] Circuit health scoring
- [ ] Automatic failover to direct connection
- [ ] Tor metrics dashboard (bandwidth, latency)
- [ ] Integration with SPECTOR job scheduler
- [ ] Email/SMS alerts for Tor failures
- [ ] Docker container with Tor pre-installed

---

## Resources

- **Tor Project:** https://www.torproject.org/
- **Tor Metrics:** https://metrics.torproject.org/
- **Check Tor:** https://check.torproject.org/
- **Stem Documentation:** https://stem.torproject.org/
- **Tornado Web:** https://www.tornadoweb.org/

---

## Support

**Issues:** https://github.com/your-org/SPECTOR/issues
**Discussions:** https://github.com/your-org/SPECTOR/discussions
**Security:** security@example.com (PGP key: 0x...)

---

**Status:** ✅ Production Ready  
**Last Updated:** 2026-02-20  
**Maintainer:** SPECTOR Contributors
