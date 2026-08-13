from flask import Flask, render_template, request
import boto3
import gzip
from datetime import datetime, timedelta, timezone


app = Flask(__name__)


# ============================================================
# AWS / S3
# ============================================================

BUCKET = "hw-project-alb-logs"

s3 = boto3.client("s3")


# ============================================================
# Timezone
# ============================================================

UTC = timezone.utc

KST = timezone(
    timedelta(hours=9)
)


# ============================================================
# Pagination
# ============================================================

PER_PAGE = 20


# ============================================================
# ALB Log timestamp parsing
# ============================================================

def parse_log_time(value):

    try:

        return datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(
            tzinfo=UTC
        )

    except ValueError:

        try:

            return datetime.strptime(
                value,
                "%Y-%m-%dT%H:%M:%SZ"
            ).replace(
                tzinfo=UTC
            )

        except ValueError:

            return None


# ============================================================
# S3 Log Files
# ============================================================

def get_log_files(
    query_start,
    query_end
):

    files = []

    paginator = s3.get_paginator(
        "list_objects_v2"
    )

    # --------------------------------------------------------
    # ALB log 파일은 실제 요청시간과
    # S3 LastModified 시간이 완전히 같다고
    # 보장할 수 없으므로 여유를 둔다.
    # --------------------------------------------------------

    file_start = (
        query_start
        - timedelta(hours=2)
    )

    file_end = (
        query_end
        + timedelta(hours=2)
    )

    # --------------------------------------------------------
    # S3 list_objects_v2 자체도 내부적으로
    # 여러 페이지를 가지고 있으므로 paginator 사용
    # --------------------------------------------------------

    for page in paginator.paginate(
        Bucket=BUCKET,
        Prefix="AWSLogs/"
    ):

        for obj in page.get(
            "Contents",
            []
        ):

            key = obj["Key"]

            if not key.endswith(
                ".log.gz"
            ):
                continue

            last_modified = obj[
                "LastModified"
            ]

            if last_modified < file_start:

                continue

            if last_modified > file_end:

                continue

            files.append(obj)

    return files


# ============================================================
# Read ALB Logs
# ============================================================

def get_logs(
    start_time=None,
    end_time=None,
    hours=1
):

    now = datetime.now(UTC)

    # ========================================================
    # Query Time
    # ========================================================

    if (
        start_time is not None
        and end_time is not None
    ):

        query_start = start_time
        query_end = end_time

    else:

        query_end = now

        query_start = (
            now
            - timedelta(hours=hours)
        )

    # ========================================================
    # S3 Files
    # ========================================================

    files = get_log_files(
        query_start,
        query_end
    )

    if not files:

        return None, []


    # ========================================================
    # Latest File
    # ========================================================

    latest_file = max(
        files,
        key=lambda x: x["LastModified"]
    )


    # ========================================================
    # Logs
    # ========================================================

    logs = []


    for file in files:

        key = file["Key"]

        try:

            response = s3.get_object(
                Bucket=BUCKET,
                Key=key
            )

            compressed_data = (
                response["Body"].read()
            )

            content = gzip.decompress(
                compressed_data
            ).decode(
                "utf-8",
                errors="replace"
            )

        except Exception as e:

            print(
                f"[ERROR] "
                f"로그 파일 읽기 실패: {key}"
            )

            print(e)

            continue


        # ====================================================
        # Parse each log
        # ====================================================

        for line in content.splitlines():

            if not line.strip():

                continue


            parts = line.split()


            if len(parts) < 15:

                continue


            # ------------------------------------------------
            # Timestamp
            # ------------------------------------------------

            log_time_string = parts[1]

            log_time = parse_log_time(
                log_time_string
            )


            if log_time is None:

                continue


            # ------------------------------------------------
            # Actual log time filtering
            # ------------------------------------------------

            if log_time < query_start:

                continue


            if log_time > query_end:

                continue


            # ------------------------------------------------
            # Request
            # ------------------------------------------------

            request_value = " ".join(
                parts[12:15]
            )


            # ------------------------------------------------
            # Save
            # ------------------------------------------------

            logs.append({

                "time": log_time_string,

                "client": parts[3],

                "target": parts[4],

                "elb_status": parts[8],

                "target_status": parts[9],

                "request": request_value,

                "source_file": key

            })


    # ========================================================
    # Newest first
    # ========================================================

    logs.sort(
        key=lambda x: x["time"],
        reverse=True
    )


    return latest_file, logs


# ============================================================
# Main
# ============================================================

@app.route("/")
def index():

    # ========================================================
    # Mode
    # ========================================================

    mode = request.args.get(
        "mode",
        "recent"
    )


    # ========================================================
    # Recent Range
    # ========================================================

    range_value = request.args.get(
        "range",
        "1"
    )


    try:

        hours = int(
            range_value
        )

    except ValueError:

        hours = 1


    if hours not in [
        1,
        3,
        6,
        24
    ]:

        hours = 1


    # ========================================================
    # Custom Date / Time
    # ========================================================

    start_date = request.args.get(
        "start_date",
        ""
    )

    start_clock = request.args.get(
        "start_time",
        ""
    )

    end_date = request.args.get(
        "end_date",
        ""
    )

    end_clock = request.args.get(
        "end_time",
        ""
    )


    custom_start = None
    custom_end = None

    custom_error = None


    # ========================================================
    # Custom Time
    # ========================================================

    if mode == "custom":

        try:

            start_kst = datetime.strptime(
                f"{start_date} {start_clock}",
                "%Y-%m-%d %H:%M"
            ).replace(
                tzinfo=KST
            )


            end_kst = datetime.strptime(
                f"{end_date} {end_clock}",
                "%Y-%m-%d %H:%M"
            ).replace(
                tzinfo=KST
            )


            custom_start = (
                start_kst.astimezone(
                    UTC
                )
            )


            custom_end = (
                end_kst.astimezone(
                    UTC
                )
            )


            if custom_end <= custom_start:

                custom_error = (
                    "종료 시간은 시작 시간보다 "
                    "뒤에 있어야 합니다."
                )

                custom_start = None
                custom_end = None


        except ValueError:

            custom_error = (
                "날짜와 시간을 올바르게 입력해주세요."
            )


    # ========================================================
    # Get Logs
    # ========================================================

    if (
        mode == "custom"
        and custom_start is not None
        and custom_end is not None
    ):

        latest_file, logs = get_logs(
            start_time=custom_start,
            end_time=custom_end
        )

    else:

        latest_file, logs = get_logs(
            hours=hours
        )


    # ========================================================
    # Statistics
    #
    # 검색/상태 필터와 관계없이
    # 현재 시간 범위 전체 로그 기준
    # ========================================================

    total = len(logs)


    status_2xx = sum(
        1
        for log in logs
        if log["elb_status"].startswith("2")
    )


    status_3xx = sum(
        1
        for log in logs
        if log["elb_status"].startswith("3")
    )


    status_4xx = sum(
        1
        for log in logs
        if log["elb_status"].startswith("4")
    )


    status_5xx = sum(
        1
        for log in logs
        if log["elb_status"].startswith("5")
    )


    # ========================================================
    # Status Filter
    # ========================================================

    status_filter = request.args.get(
        "status",
        "all"
    )


    filtered_logs = logs


    if status_filter != "all":

        filtered_logs = [

            log

            for log in filtered_logs

            if log["elb_status"].startswith(
                status_filter
            )

        ]


    # ========================================================
    # Search
    # ========================================================

    search = request.args.get(
        "search",
        ""
    ).strip().lower()


    if search:

        filtered_logs = [

            log

            for log in filtered_logs

            if search in (
                log["client"]
                + " "
                + log["target"]
                + " "
                + log["request"]
            ).lower()

        ]


    # ========================================================
    # Pagination
    # ========================================================

    total_filtered = len(
        filtered_logs
    )


    total_pages = max(
        1,
        (
            total_filtered
            + PER_PAGE
            - 1
        ) // PER_PAGE
    )


    page = request.args.get(
        "page",
        1,
        type=int
    )


    if page < 1:

        page = 1


    if page > total_pages:

        page = total_pages


    start_index = (
        page - 1
    ) * PER_PAGE


    end_index = (
        start_index
        + PER_PAGE
    )


    paginated_logs = filtered_logs[
        start_index:end_index
    ]


    # ========================================================
    # Render
    # ========================================================

    return render_template(

        "index.html",

        latest_file=latest_file,

        total=total,

        status_2xx=status_2xx,

        status_3xx=status_3xx,

        status_4xx=status_4xx,

        status_5xx=status_5xx,

        logs=paginated_logs,

        status_filter=status_filter,

        search=search,

        range_value=str(hours),

        mode=mode,

        start_date=start_date,

        start_time=start_clock,

        end_date=end_date,

        end_time=end_clock,

        page=page,

        total_pages=total_pages,

        total_filtered=total_filtered,

        per_page=PER_PAGE,

        custom_error=custom_error

    )


# ============================================================
# Flask
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5001,

        debug=True

    )