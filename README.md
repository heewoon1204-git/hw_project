# ☁️ AWS EKS 기반 클라우드 인프라 운영 실습

AWS와 Kubernetes를 기반으로 웹 서비스를 구축하고,
**모니터링 → 장애 발생 → 장애 감지 → 복구** 과정을 직접 구현하고 검증하는 개인 프로젝트입니다.

단순한 인프라 구축에 그치지 않고, 실제 운영 환경에서 발생할 수 있는 장애 상황을 의도적으로 재현하고 Kubernetes와 AWS가 이를 어떻게 처리하는지 확인하는 것을 목표로 합니다.

---

## 🎯 Project Goal

* AWS 기반 클라우드 인프라 직접 구축
* Kubernetes(EKS) 환경 구성 및 운영
* 컨테이너 간 통신 구조 이해
* 애플리케이션 상태 및 인프라 모니터링
* 장애 상황 직접 재현
* Kubernetes의 Self-healing 및 Auto Scaling 검증
* 장애 발생 원인과 해결 과정 기록
* Terraform을 활용한 인프라 코드화

---

## 🏗️ Architecture

### 현재 계획

```text
                         Internet
                            │
                            ▼
                        Route 53
                            │
                            ▼
                           ALB
                            │
                            ▼
                      ┌───────────┐
                      │    EKS    │
                      └─────┬─────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
       Private Subnet A             Private Subnet C
              │                           │
          EKS Node A                  EKS Node B
              │                           │
        ┌─────┴─────┐             ┌─────┴─────┐
        │           │             │           │
    Frontend     Backend       Frontend     Backend
       Pod          Pod           Pod          Pod
                     │
               ┌─────┴─────┐
               │           │
             Redis         RDS
```

### Monitoring

```text
EKS
 │
 ├── Application
 │
 └── Monitoring
      ├── Prometheus
      ├── Grafana
      └── Alertmanager
```

> 아키텍처는 프로젝트 진행 과정에서 변경될 수 있습니다.

---

## ☁️ AWS Infrastructure

| Component          | Purpose                   |
| ------------------ | ------------------------- |
| VPC                | 전체 네트워크 구성                |
| Public Subnet      | ALB 배치                    |
| Private Subnet     | EKS Worker Node 배치        |
| Internet Gateway   | Public Subnet 인터넷 통신      |
| VPC Endpoint       | NAT Gateway 없이 AWS 서비스 접근 |
| EKS                | Kubernetes Cluster        |
| Managed Node Group | Worker Node 관리            |
| ALB                | 외부 트래픽 전달                 |
| ECR                | Container Image 저장        |
| Route 53           | Domain 관리                 |
| ACM                | HTTPS 인증서                 |
| IAM                | AWS 리소스 권한 관리             |
| SSM                | Private Node 관리           |

### Network

```text
VPC
├── Public Subnet A
├── Public Subnet C
├── Private Subnet A
└── Private Subnet C

NAT Gateway
└── 사용하지 않음

VPC Endpoint
└── 필요한 AWS 서비스에 Private 연결
```

---

## ☸️ Kubernetes

구현 예정:

* Deployment
* ReplicaSet
* Pod
* Service
* Ingress
* ConfigMap
* Secret
* HPA
* PV / PVC

### Application

```text
Frontend
    │
    ▼
Backend
    │
 ┌──┴───┐
 ▼      ▼
Redis   RDS
```

---

## 📊 Monitoring

Prometheus와 Grafana를 이용하여 다음 항목을 모니터링합니다.

* Node CPU / Memory
* Pod CPU / Memory
* Pod 상태
* Pod 개수
* Request Rate
* Error Rate
* Network
* HPA Scale Out

---

## 🚨 Failure Scenarios

의도적으로 장애를 발생시켜 Kubernetes의 복구 동작을 검증합니다.

### 1. Pod 장애

```text
Pod 삭제
   ↓
ReplicaSet 감지
   ↓
새로운 Pod 생성
   ↓
서비스 복구
```

### 2. CPU 부하

```text
CPU 증가
   ↓
Metrics 수집
   ↓
HPA 감지
   ↓
Pod Scale Out
```

### 3. Redis 장애

```text
Redis Pod 장애
   ↓
Backend 연결 실패
   ↓
장애 감지
   ↓
Redis 복구
   ↓
서비스 정상화
```

### 4. Network 장애

Backend와 Redis 간 통신을 제한하여 네트워크 장애 상황을 재현합니다.

### 5. Node 장애

Worker Node 장애 상황에서 Pod가 어떻게 처리되는지 확인합니다.

---

## 🔎 Troubleshooting

장애가 발생했을 때 다음 과정으로 원인을 분석합니다.

```text
문제 발생
   ↓
Monitoring 확인
   ↓
Pod / Node 상태 확인
   ↓
Event 확인
   ↓
Log 확인
   ↓
Network 확인
   ↓
원인 분석
   ↓
조치
   ↓
복구 여부 확인
```

장애별 상세 분석은 `docs/troubleshooting/`에 기록합니다.

---

## 📚 Project Progress

* [ ] AWS VPC 구성
* [ ] Public / Private Subnet 구성
* [ ] Route Table / Internet Gateway 구성
* [ ] Security Group 구성
* [ ] VPC Endpoint 구성
* [ ] EKS Cluster 구성
* [ ] EKS Managed Node Group 구성
* [ ] ECR 구성
* [ ] ALB 구성
* [ ] Route 53 / ACM 구성
* [ ] Frontend 구성
* [ ] Backend 구성
* [ ] Redis 구성
* [ ] RDS PostgreSQL 구성
* [ ] Kubernetes Service 구성
* [ ] Ingress 구성
* [ ] PV / PVC 구성
* [ ] Prometheus 구성
* [ ] Grafana 구성
* [ ] HPA 구성
* [ ] 장애 시나리오 구현
* [ ] 장애 자동 복구 검증
* [ ] Terraform으로 IaC 구성
* [ ] CI/CD 구성

---

## 📝 Documentation

프로젝트를 진행하면서 학습 내용과 장애 분석 과정을 기록합니다.

```text
docs/
├── architecture/
├── aws/
├── kubernetes/
├── monitoring/
└── troubleshooting/
```

---

## 🛠️ Tech Stack

### Cloud

* AWS
* VPC
* EKS
* ALB
* RDS
* ECR
* S3

### Kubernetes

* Kubernetes
* Helm

### Monitoring

* Prometheus
* Grafana
* Alertmanager

### Infrastructure as Code

* Terraform

### CI/CD

* GitHub Actions

### Application

* Frontend
* Backend
* Redis
* PostgreSQL
