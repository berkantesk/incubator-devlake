import json

# Define Panel 1: Individual Contributor Performance (Commits, PRs, Incidents)
contributor_panel = {
  "datasource": "mysql",
  "fieldConfig": {
    "defaults": {
      "color": { "mode": "thresholds" },
      "custom": { "align": "auto", "displayMode": "auto" },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [ { "color": "green", "value": None } ]
      }
    },
    "overrides": []
  },
  "gridPos": { "h": 10, "w": 12, "x": 0, "y": 70 },
  "id": 999,
  "options": {
    "footer": { "fields": "", "reducer": ["sum"], "show": False },
    "showHeader": True,
    "sortBy": [ { "desc": True, "displayName": "Commits" } ]
  },
  "pluginVersion": "8.4.3",
  "targets": [
    {
      "datasource": "mysql",
      "format": "table",
      "group": [],
      "metricColumn": "none",
      "rawQuery": True,
      "rawSql": """WITH 
_commits AS (
  SELECT author_name, count(distinct sha) as commit_count
  FROM commits c
  JOIN repo_commits rc ON c.sha = rc.commit_sha
  JOIN project_mapping pm ON rc.repo_id = pm.row_id
  WHERE pm.project_name IN (${project}) AND $__timeFilter(authored_date)
  GROUP BY 1
),
_prs AS (
  SELECT author_name, 
         count(*) as pr_opened,
         sum(case when status = 'MERGED' then 1 else 0 end) as pr_merged
  FROM pull_requests pr
  JOIN project_mapping pm ON pr.base_repo_id = pm.row_id
  WHERE pm.project_name IN (${project}) AND $__timeFilter(created_date)
  GROUP BY 1
),
_incidents_fixed AS (
  SELECT assignee_name as author_name, count(*) as incidents_fixed
  FROM incidents i
  JOIN project_mapping pm ON i.scope_id = pm.row_id
  WHERE pm.project_name IN (${project}) 
    AND $__timeFilter(resolution_date)
  GROUP BY 1
),
_incidents_caused AS (
  SELECT c.author_name, count(distinct i.id) as incidents_caused
  FROM incidents i
  JOIN project_incident_deployment_relationships pim ON i.id = pim.id
  JOIN cicd_deployment_commits cdc ON pim.deployment_id = cdc.cicd_deployment_id
  JOIN commits c ON cdc.commit_sha = c.sha
  JOIN project_mapping pm ON i.scope_id = pm.row_id
  WHERE pm.project_name IN (${project}) 
    AND $__timeFilter(i.created_date)
  GROUP BY 1
),
_all_authors AS (
    SELECT author_name FROM _commits 
    UNION SELECT author_name FROM _prs 
    UNION SELECT author_name FROM _incidents_fixed
    UNION SELECT author_name FROM _incidents_caused
)

SELECT 
  t.author_name as 'Engineer',
  COALESCE(c.commit_count, 0) as 'Commits',
  COALESCE(p.pr_opened, 0) as 'PRs Opened',
  COALESCE(p.pr_merged, 0) as 'PRs Merged',
  COALESCE(f.incidents_fixed, 0) as 'Incidents Resolved',
  COALESCE(caused.incidents_caused, 0) as 'Incidents Caused'
FROM _all_authors t
LEFT JOIN _commits c ON t.author_name = c.author_name
LEFT JOIN _prs p ON t.author_name = p.author_name
LEFT JOIN _incidents_fixed f ON t.author_name = f.author_name
LEFT JOIN _incidents_caused caused ON t.author_name = caused.author_name
WHERE t.author_name IS NOT NULL AND t.author_name != ''
ORDER BY 'Commits' DESC
LIMIT 100""",
      "refId": "A"
    }
  ],
  "title": "Individual Contributor Performance",
  "type": "table"
}

# Define Panel 2: Reviewer Leaderboard
reviewer_panel = {
  "datasource": "mysql",
  "fieldConfig": {
    "defaults": {
      "color": { "mode": "thresholds" },
      "custom": { "align": "auto", "displayMode": "auto" },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [ { "color": "blue", "value": None } ]
      }
    },
    "overrides": []
  },
  "gridPos": { "h": 10, "w": 12, "x": 12, "y": 70 },
  "id": 1000,
  "options": {
    "footer": { "fields": "", "reducer": ["sum"], "show": False },
    "showHeader": True,
    "sortBy": [ { "desc": True, "displayName": "PRs Reviewed" } ]
  },
  "pluginVersion": "8.4.3",
  "targets": [
    {
      "datasource": "mysql",
      "format": "table",
      "group": [],
      "metricColumn": "none",
      "rawQuery": True,
      "rawSql": """SELECT 
  prc.author_name as 'Reviewer',
  count(distinct pr.id) as 'PRs Reviewed',
  count(*) as 'Comments Given'
FROM pull_request_comments prc
JOIN pull_requests pr ON prc.pull_request_id = pr.id
JOIN project_mapping pm ON pr.base_repo_id = pm.row_id AND pm.table = 'repos'
WHERE pm.project_name IN (${project})
  AND prc.author_id != pr.author_id
  AND $__timeFilter(prc.created_date)
GROUP BY 1
ORDER BY 2 DESC
LIMIT 100""",
      "refId": "A"
    }
  ],
  "title": "Reviewer Leaderboard",
  "type": "table"
}

# Read existing dashboard
try:
    with open('grafana/dashboards/EngineeringOverview.json', 'r') as f:
        dashboard = json.load(f)

    # Remove existing custom panels if they exist (to avoid duplicates)
    dashboard['panels'] = [p for p in dashboard['panels'] if p['id'] not in [999, 1000]]

    # Append new panels
    dashboard['panels'].append(contributor_panel)
    dashboard['panels'].append(reviewer_panel)

    # Save updated dashboard
    with open('grafana/dashboards/EngineeringOverview.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print("Dashboard updated successfully.")
except Exception as e:
    print(f"Error: {e}")