import json
import subprocess

# Read the updated dashboard file
with open('grafana/dashboards/EngineeringOverview.json', 'r') as f:
    dashboard = json.load(f)

# Modify metadata to create a new dashboard copy
dashboard['uid'] = 'engineering-overview-custom'
dashboard['title'] = 'Engineering Overview - Custom'
dashboard['id'] = None  # Reset ID to create new

# Create payload
payload = {
    "dashboard": dashboard,
    "overwrite": True
}

# Write payload to file
with open('grafana/dashboards/custom_upload_payload.json', 'w') as f:
    json.dump(payload, f)

print("Created custom payload.")
