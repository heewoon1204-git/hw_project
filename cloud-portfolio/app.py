from flask import Flask, render_template, jsonify
import requests
import markdown
import os
import psycopg


app = Flask(__name__)


# ============================================================
# GitHub Repository Settings
# ============================================================

GITHUB_OWNER = "heewoon1204-git"
GITHUB_REPO = "infra_study"

GITHUB_API_BASE_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/contents"
)


# ============================================================
# GitHub API Helper
# ============================================================

def get_github_contents(path=""):
    """
    GitHub Repository의 파일/폴더 정보를 가져온다.

    path가 비어 있으면 Repository root를 조회하고,
    path가 있으면 해당 디렉터리 또는 파일을 조회한다.
    """

    if path:
        url = f"{GITHUB_API_BASE_URL}/{path}"
    else:
        url = GITHUB_API_BASE_URL

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# PostgreSQL Connection
# ============================================================

def get_db_connection():
    """
    Kubernetes Secret으로 주입된 환경변수를 이용해
    RDS PostgreSQL에 연결한다.
    """

    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "postgres"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=5,
    )


# ============================================================
# Home
# ============================================================

@app.route("/")
def index():
    """
    Portfolio 메인 페이지
    """

    return render_template(
        "index.html"
    )


# ============================================================
# Resume
# ============================================================

@app.route("/resume")
def resume():
    """
    경력기술서 / 이력서 페이지
    """

    return render_template(
        "resume.html"
    )


# ============================================================
# Project
# ============================================================

@app.route("/project")
def project():
    """
    프로젝트 소개 페이지
    """

    return render_template(
        "project.html"
    )


# ============================================================
# Architecture
# ============================================================

@app.route("/architecture")
def architecture():
    """
    AWS / EKS Architecture 페이지
    """

    return render_template(
        "architecture.html"
    )


# ============================================================
# Monitoring
# ============================================================

@app.route("/monitoring")
def monitoring():
    """
    Monitoring 선택 페이지
    """

    return render_template(
        "monitoring.html"
    )


# ============================================================
# Study - Category List
# ============================================================

@app.route("/study")
def study():
    """
    GitHub infra_study Repository의
    최상위 디렉터리를 가져온다.

    예:
        aws
        docker
        k8s
    """

    items = get_github_contents()

    categories = [
        item
        for item in items
        if item["type"] == "dir"
    ]

    return render_template(
        "study.html",
        categories=categories
    )


# ============================================================
# Study - Documents in Category
# ============================================================

@app.route("/study/<category>")
def study_category(category):
    """
    GitHub의 특정 카테고리 디렉터리 안에 있는
    Markdown 파일 목록을 가져온다.

    예:
        /study/aws
        /study/docker
        /study/k8s
    """

    items = get_github_contents(
        category
    )

    documents = [
        item
        for item in items
        if (
            item["type"] == "file"
            and item["name"].lower().endswith(
                (".md", ".markdown")
            )
        )
    ]

    return render_template(
        "study-category.html",
        category=category,
        documents=documents
    )


# ============================================================
# Study - Markdown Document
# ============================================================

@app.route("/study/<category>/<path:filename>")
def study_document(category, filename):
    """
    GitHub에서 Markdown 파일 내용을 가져와
    HTML로 변환한 뒤 웹페이지에 표시한다.

    예:
        /study/k8s/ingress.md
    """

    # GitHub Repository 내부 경로
    path = f"{category}/{filename}"

    # GitHub API를 통해 파일 정보 조회
    item = get_github_contents(
        path
    )

    # 파일이 아닌 경우
    if item["type"] != "file":
        return "Document not found", 404

    # Markdown 파일인지 확인
    if not item["name"].lower().endswith(
        (".md", ".markdown")
    ):
        return "Unsupported document type", 400

    # GitHub에서 원본 Markdown 다운로드
    response = requests.get(
        item["download_url"],
        timeout=10
    )

    response.raise_for_status()

    markdown_content = response.text

    # Markdown → HTML 변환
    markdown_html = markdown.markdown(
        markdown_content,
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "toc"
        ]
    )

    return render_template(
        "study-document.html",
        category=category,
        filename=filename,
        markdown_html=markdown_html
    )


# ============================================================
# Database Health Check
# ============================================================

@app.route("/api/db-health")
def db_health():

    try:
        with get_db_connection() as conn:

            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()

        if result == (1,):
            return jsonify({
                "database": "connected"
            }), 200

        return jsonify({
            "database": "unexpected_response"
        }), 500

    except Exception as e:

        print(type(e).__name__)
        print(e)

        return jsonify({
            "database": "disconnected",
            "detail": str(e)
        }), 503


# ============================================================
# Incidents - List
# ============================================================

@app.route("/api/incidents", methods=["GET"])
def get_incidents():

    try:
        with get_db_connection() as conn:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        id,
                        incident_type,
                        status,
                        description,
                        started_at,
                        resolved_at,
                        root_cause,
                        resolution
                    FROM incidents
                    ORDER BY started_at DESC
                """)

                rows = cur.fetchall()

                incidents = []

                for row in rows:

                    incidents.append({
                        "id": row[0],
                        "incident_type": row[1],
                        "status": row[2],
                        "description": row[3],
                        "started_at": (
                            row[4].isoformat()
                            if row[4]
                            else None
                        ),
                        "resolved_at": (
                            row[5].isoformat()
                            if row[5]
                            else None
                        ),
                        "root_cause": row[6],
                        "resolution": row[7],
                    })

        return jsonify(
            incidents
        ), 200

    except Exception as e:

        print(type(e).__name__)
        print(e)

        return jsonify({
            "error": "Failed to fetch incidents",
            "detail": str(e)
        }), 500


# ============================================================
# Application Start
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )