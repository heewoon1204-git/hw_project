#!/bin/bash

BUCKET="hw-project-alb-logs"
PROFILE="hw-infra"

echo "===== ALB Access Log ====="
echo

# 가장 최근 로그 파일 찾기
FILE=$(aws s3 ls "s3://${BUCKET}/" \
  --recursive \
  --profile "$PROFILE" \
  | sort \
  | tail -1 \
  | awk '{print $4}')

if [ -z "$FILE" ]; then
    echo "ALB log file not found."
    exit 1
fi

echo "Latest log:"
echo "$FILE"
echo

# 로그 다운로드 → 압축 해제 → 기본 필드 출력
aws s3 cp "s3://${BUCKET}/${FILE}" - \
  --profile "$PROFILE" \
  | gzip -dc \
  | awk '{
      print "TIME:", $2
      print "CLIENT:", $4
      print "TARGET:", $5
      print "ELB_STATUS:", $9
      print "TARGET_STATUS:", $10
      print "REQUEST:", $13, $14, $15
      print "----------------------------------------"
  }'
