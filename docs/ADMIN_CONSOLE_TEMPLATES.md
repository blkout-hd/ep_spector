# SPECTOR Admin Console Templates

The admin console HTML templates are located in the `docs/` directory:

- `admin_login.html` - Authentication page
- `admin_dashboard.html` - Main dashboard with real-time metrics

## Installation

For production deployment, you may want to create a `src/python/templates/` directory and copy these files:

```bash
mkdir -p src/python/templates
cp docs/admin_login.html src/python/templates/login.html
cp docs/admin_dashboard.html src/python/templates/admin_dashboard.html
```

The admin console will automatically look for templates in:
1. `docs/` directory (current setup)
2. `src/python/templates/` directory (fallback)

## Usage

Start the admin console:

```bash
python launcher.py admin --port 8888 --host localhost
```

Default credentials:
- Username: `admin`
- Password: `spector`

Access the dashboard at: http://localhost:8888

## Customization

You can customize credentials by setting environment variables or passing arguments to the TornadoAdminServer class.
