# IAM Identity Center 

## IAM Identity Center 이용해서 로그인

여러 AWS 계정의 사용자 로그인을 한 곳에서 관리하는 서비스

관리자, 개발자용 User 생성 및 그에 맞는 Permission Sets 구성

```bash
IAM Identity Center
│
├── Users
│   ├── admin
│   └── developer
│
├── Groups
│   ├── Admins
│   └── Developers
│
└── Permission Sets
    ├── Admin
    │   └── AdministratorAccess
    │
    └── Developer
        └── ReadOnlyAccess
```

### 1. IAM Identity Center Enable

싱글 리전(서울) 선택

### 2. group,user 만들기

IAM Identity Center → Dashbord → Groups → create group

IAM Identity Center → Dashbord → Users → Add user

### 3. Permission Set 만들기

IAM Identity Center → Multi-account permissions → Permission sets → Create permission set

```bash
# 관리자용
types : Predefined permission set
Policy for predefined permission set : AdministratorAccess

# 조회 권한만 있는 개발자용
types : Predefined permission set
Policy for predefined permission set : AdministratorAccess
```

### 4. Group에 Permission Set 붙이기

### 5. 접속

주소 : https://d-9b675b3cc8.awsapps.com/start



### IAM user vs Identity Center

IAM User : 계정마다 IAM User 생성 <br>
Identity Center : 사용자는 한 번만 만들고, 어느 AWS 계정에 어떤 권한으로 들어갈지를 관리 가능

```bash
# IAM User

AWS Account
 ├── IAM User: heewoon
 ├── IAM User: kim
 └── IAM User: admin

 # Identity Center

 Identity Center
 ├── User: heewoon
 └── Group: Developer
          │
          ├── Dev Account → PowerUser
          └── Prod Account → ReadOnly
```