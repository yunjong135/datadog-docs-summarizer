import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Datadog Docs 주요 페이지 인덱스
DOCS_INDEX = [
    # APM / Tracing
    {"title": "APM & Distributed Tracing", "url": "https://docs.datadoghq.com/tracing/", "tags": ["apm", "tracing", "distributed", "trace"]},
    {"title": "Getting Started with APM Tracing", "url": "https://docs.datadoghq.com/getting_started/tracing/", "tags": ["apm", "tracing", "getting started", "setup"]},
    {"title": "APM Setup & Configuration", "url": "https://docs.datadoghq.com/tracing/trace_collection/", "tags": ["apm", "tracing", "setup", "configuration", "install"]},
    {"title": "Trace Explorer", "url": "https://docs.datadoghq.com/tracing/trace_explorer/", "tags": ["apm", "tracing", "explorer", "search", "query"]},
    {"title": "Service Catalog", "url": "https://docs.datadoghq.com/tracing/service_catalog/", "tags": ["apm", "service catalog", "service"]},
    {"title": "Continuous Profiler", "url": "https://docs.datadoghq.com/profiler/", "tags": ["profiler", "profiling", "cpu", "memory", "performance"]},
    {"title": "Application Vulnerability Management", "url": "https://docs.datadoghq.com/security/application_security/", "tags": ["security", "vulnerability", "appsec", "application security"]},

    # Logs
    {"title": "Log Management", "url": "https://docs.datadoghq.com/logs/", "tags": ["logs", "log management", "logging"]},
    {"title": "Log Collection & Integrations", "url": "https://docs.datadoghq.com/logs/log_collection/", "tags": ["logs", "collection", "integration", "ingest"]},
    {"title": "Log Explorer", "url": "https://docs.datadoghq.com/logs/explorer/", "tags": ["logs", "explorer", "search", "query", "filter"]},
    {"title": "Log Pipelines & Processing", "url": "https://docs.datadoghq.com/logs/log_configuration/pipelines/", "tags": ["logs", "pipeline", "processing", "parsing", "grok"]},
    {"title": "Log Indexes & Archiving", "url": "https://docs.datadoghq.com/logs/log_configuration/indexes/", "tags": ["logs", "index", "archive", "retention", "storage"]},
    {"title": "Log-based Metrics", "url": "https://docs.datadoghq.com/logs/log_configuration/logs_to_metrics/", "tags": ["logs", "metrics", "log to metric"]},
    {"title": "Sensitive Data Scanner", "url": "https://docs.datadoghq.com/sensitive_data_scanner/", "tags": ["logs", "sensitive data", "pii", "scanner", "redaction"]},
    {"title": "Audit Trail", "url": "https://docs.datadoghq.com/account_management/audit_trail/", "tags": ["audit", "audit trail", "compliance", "logs"]},

    # Metrics
    {"title": "Metrics", "url": "https://docs.datadoghq.com/metrics/", "tags": ["metrics", "timeseries"]},
    {"title": "Metrics Summary", "url": "https://docs.datadoghq.com/metrics/summary/", "tags": ["metrics", "summary", "explorer"]},
    {"title": "Custom Metrics", "url": "https://docs.datadoghq.com/metrics/custom_metrics/", "tags": ["metrics", "custom metrics", "statsd", "dogstatsd"]},
    {"title": "DogStatsD", "url": "https://docs.datadoghq.com/developers/dogstatsd/", "tags": ["dogstatsd", "statsd", "metrics", "custom", "udp"]},
    {"title": "Metrics without Limits", "url": "https://docs.datadoghq.com/metrics/metrics-without-limits/", "tags": ["metrics", "cardinality", "cost", "tag filtering"]},

    # Monitors & Alerts
    {"title": "Monitors", "url": "https://docs.datadoghq.com/monitors/", "tags": ["monitors", "alerts", "alerting", "notifications"]},
    {"title": "Create a Monitor", "url": "https://docs.datadoghq.com/monitors/create/", "tags": ["monitors", "create", "setup", "alert"]},
    {"title": "Monitor Types", "url": "https://docs.datadoghq.com/monitors/types/", "tags": ["monitors", "types", "metric monitor", "log monitor", "apm monitor"]},
    {"title": "Alerting Notifications", "url": "https://docs.datadoghq.com/monitors/notify/", "tags": ["monitors", "notifications", "alert", "slack", "email", "pagerduty"]},
    {"title": "Downtimes & SLOs", "url": "https://docs.datadoghq.com/monitors/downtimes/", "tags": ["monitors", "downtime", "maintenance", "mute"]},
    {"title": "Service Level Objectives (SLO)", "url": "https://docs.datadoghq.com/service_management/slos/", "tags": ["slo", "service level", "reliability", "uptime"]},

    # Infrastructure & Agent
    {"title": "Datadog Agent", "url": "https://docs.datadoghq.com/agent/", "tags": ["agent", "install", "setup", "datadog agent"]},
    {"title": "Agent Installation", "url": "https://docs.datadoghq.com/agent/basic_agent_usage/", "tags": ["agent", "install", "linux", "windows", "mac", "setup"]},
    {"title": "Infrastructure Monitoring", "url": "https://docs.datadoghq.com/infrastructure/", "tags": ["infrastructure", "hosts", "containers", "servers"]},
    {"title": "Host Map", "url": "https://docs.datadoghq.com/infrastructure/hostmap/", "tags": ["infrastructure", "host map", "visualization"]},
    {"title": "Container Monitoring", "url": "https://docs.datadoghq.com/containers/", "tags": ["containers", "docker", "kubernetes", "container monitoring"]},
    {"title": "Kubernetes Monitoring", "url": "https://docs.datadoghq.com/containers/kubernetes/", "tags": ["kubernetes", "k8s", "containers", "pods", "cluster"]},
    {"title": "Docker Integration", "url": "https://docs.datadoghq.com/containers/docker/", "tags": ["docker", "containers", "integration"]},
    {"title": "Process Monitoring", "url": "https://docs.datadoghq.com/infrastructure/process/", "tags": ["process", "process monitoring", "live processes"]},
    {"title": "Network Performance Monitoring", "url": "https://docs.datadoghq.com/network_monitoring/performance/", "tags": ["network", "npm", "network monitoring", "traffic"]},
    {"title": "Cloud Cost Management", "url": "https://docs.datadoghq.com/cloud_cost_management/", "tags": ["cost", "cloud cost", "aws cost", "billing"]},

    # Dashboards
    {"title": "Dashboards", "url": "https://docs.datadoghq.com/dashboards/", "tags": ["dashboards", "visualization", "widgets"]},
    {"title": "Dashboard Widgets", "url": "https://docs.datadoghq.com/dashboards/widgets/", "tags": ["dashboards", "widgets", "graphs", "timeseries", "query value"]},
    {"title": "Template Variables", "url": "https://docs.datadoghq.com/dashboards/template_variables/", "tags": ["dashboards", "template variables", "filters", "dynamic"]},
    {"title": "Notebooks", "url": "https://docs.datadoghq.com/notebooks/", "tags": ["notebooks", "collaboration", "investigation"]},

    # Synthetics / RUM
    {"title": "Synthetic Monitoring", "url": "https://docs.datadoghq.com/synthetics/", "tags": ["synthetics", "synthetic monitoring", "uptime", "api test", "browser test"]},
    {"title": "Synthetic API Tests", "url": "https://docs.datadoghq.com/synthetics/api_tests/", "tags": ["synthetics", "api test", "http test", "endpoint monitoring"]},
    {"title": "Synthetic Browser Tests", "url": "https://docs.datadoghq.com/synthetics/browser_tests/", "tags": ["synthetics", "browser test", "selenium", "end to end", "e2e"]},
    {"title": "Real User Monitoring (RUM)", "url": "https://docs.datadoghq.com/real_user_monitoring/", "tags": ["rum", "real user monitoring", "frontend", "browser", "mobile"]},
    {"title": "RUM Browser Setup", "url": "https://docs.datadoghq.com/real_user_monitoring/browser/", "tags": ["rum", "browser", "javascript", "setup", "frontend monitoring"]},
    {"title": "Session Replay", "url": "https://docs.datadoghq.com/real_user_monitoring/session_replay/", "tags": ["rum", "session replay", "recording", "user session"]},
    {"title": "Core Web Vitals", "url": "https://docs.datadoghq.com/real_user_monitoring/browser/monitoring_page_performance/", "tags": ["rum", "core web vitals", "lcp", "fid", "cls", "performance"]},

    # Integrations
    {"title": "Integrations", "url": "https://docs.datadoghq.com/integrations/", "tags": ["integrations", "third party", "aws", "gcp", "azure"]},
    {"title": "AWS Integration", "url": "https://docs.datadoghq.com/integrations/amazon_web_services/", "tags": ["aws", "amazon", "integration", "cloud", "ec2", "lambda", "s3"]},
    {"title": "GCP Integration", "url": "https://docs.datadoghq.com/integrations/google_cloud_platform/", "tags": ["gcp", "google cloud", "integration", "cloud"]},
    {"title": "Azure Integration", "url": "https://docs.datadoghq.com/integrations/azure/", "tags": ["azure", "microsoft", "integration", "cloud"]},
    {"title": "Slack Integration", "url": "https://docs.datadoghq.com/integrations/slack/", "tags": ["slack", "integration", "notifications", "alerts", "chatops"]},
    {"title": "PagerDuty Integration", "url": "https://docs.datadoghq.com/integrations/pagerduty/", "tags": ["pagerduty", "integration", "oncall", "incidents", "alerts"]},
    {"title": "Kubernetes Integration", "url": "https://docs.datadoghq.com/integrations/kubernetes/", "tags": ["kubernetes", "k8s", "integration"]},
    {"title": "PostgreSQL Integration", "url": "https://docs.datadoghq.com/integrations/postgres/", "tags": ["postgres", "postgresql", "database", "integration", "sql"]},
    {"title": "MySQL Integration", "url": "https://docs.datadoghq.com/integrations/mysql/", "tags": ["mysql", "database", "integration", "sql"]},
    {"title": "Redis Integration", "url": "https://docs.datadoghq.com/integrations/redisdb/", "tags": ["redis", "cache", "integration", "database"]},
    {"title": "Nginx Integration", "url": "https://docs.datadoghq.com/integrations/nginx/", "tags": ["nginx", "web server", "integration", "http"]},

    # Database Monitoring
    {"title": "Database Monitoring", "url": "https://docs.datadoghq.com/database_monitoring/", "tags": ["database monitoring", "dbm", "query", "slow query", "postgres", "mysql"]},

    # Security
    {"title": "Cloud Security Management", "url": "https://docs.datadoghq.com/security/cloud_security_management/", "tags": ["security", "csm", "cloud security", "posture", "misconfigurations"]},
    {"title": "Cloud SIEM", "url": "https://docs.datadoghq.com/security/cloud_siem/", "tags": ["security", "siem", "threat detection", "security signals"]},

    # Incident Management
    {"title": "Incident Management", "url": "https://docs.datadoghq.com/service_management/incident_management/", "tags": ["incident", "incident management", "oncall", "postmortem"]},
    {"title": "On-Call", "url": "https://docs.datadoghq.com/service_management/on-call/", "tags": ["oncall", "on-call", "paging", "escalation"]},

    # API & SDK
    {"title": "Datadog API Reference", "url": "https://docs.datadoghq.com/api/latest/", "tags": ["api", "rest api", "sdk", "reference"]},
    {"title": "Getting Started with Datadog", "url": "https://docs.datadoghq.com/getting_started/", "tags": ["getting started", "introduction", "overview", "beginner"]},
    {"title": "Tagging", "url": "https://docs.datadoghq.com/getting_started/tagging/", "tags": ["tagging", "tags", "labels", "metadata"]},
    {"title": "OpenTelemetry", "url": "https://docs.datadoghq.com/opentelemetry/", "tags": ["opentelemetry", "otel", "otel metrics", "otel traces", "otel logs"]},
    {"title": "Unified Service Tagging", "url": "https://docs.datadoghq.com/getting_started/tagging/unified_service_tagging/", "tags": ["unified service tagging", "ust", "env", "service", "version", "tagging"]},
]


def score_result(doc: dict, query: str) -> int:
    """검색어와 문서의 관련성 점수를 계산합니다."""
    query_lower = query.lower()
    words = query_lower.split()
    score = 0

    title_lower = doc["title"].lower()
    url_lower = doc["url"].lower()
    tags = doc.get("tags", [])

    # 정확한 구문 매칭 (높은 점수)
    if query_lower in title_lower:
        score += 10
    if query_lower in url_lower:
        score += 8
    if any(query_lower == tag for tag in tags):
        score += 12

    # 부분 매칭
    for word in words:
        if len(word) < 2:
            continue
        if word in title_lower:
            score += 3
        if word in url_lower:
            score += 2
        for tag in tags:
            if word in tag:
                score += 4
            elif tag in word:
                score += 2

    return score


def get_excerpt(url: str) -> str:
    """URL에서 짧은 발췌문을 가져옵니다."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 불필요한 요소 제거
        for tag in soup(["nav", "footer", "header", "script", "style"]):
            tag.decompose()

        # meta description 우선
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"][:200]

        # 첫 번째 문단
        main = soup.find("main") or soup.find("article") or soup.find(id="main-content")
        if main:
            p = main.find("p")
            if p:
                return p.get_text(strip=True)[:200]
    except Exception:
        pass
    return ""


def search_docs(query: str) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("검색어를 입력해주세요.")

    query = query.strip()

    # 점수 계산 후 정렬
    scored = []
    for doc in DOCS_INDEX:
        s = score_result(doc, query)
        if s > 0:
            scored.append((s, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:8]

    if not top:
        return []

    results = []
    for _, doc in top:
        excerpt = get_excerpt(doc["url"])
        results.append({
            "title": doc["title"],
            "url": doc["url"],
            "excerpt": excerpt,
        })

    return results
