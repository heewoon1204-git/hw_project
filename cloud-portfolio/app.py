from flask import Flask, render_template
import requests
import markdown


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

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")

@app.route("/project")
def project():
    return render_template("project.html")


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")

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
# Application Start
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )