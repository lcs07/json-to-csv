# JSON to CSV 변환기

JSON 배열을 CSV 파일로 변환하는 Python 유틸리티입니다.

## 기능

- JSON 배열의 각 객체를 CSV 행으로 변환
- 모든 객체의 키를 자동으로 감지하여 CSV 헤더 생성
- 첫 번째 객체의 필드 순서를 유지하여 CSV 헤더 정렬
- 3가지 변환 모드: 기본, 고급 평면화, 전치 변환
- 특수 구조 자동 감지 (계층적 헤더)
- UTF-8 인코딩 지원 (한글 데이터 처리 가능)
- Python 3.12 최적화

## 파일 구조

```
json-to-csv/
├── main.py                 # Python 변환기 (메인)
├── sample_data.json        # 샘플 데이터
├── requirements.txt        # Python 의존성
├── .python-version         # pyenv Python 버전 설정
├── .gitignore              # Git 무시 파일
└── README.md               # 이 파일
```

## 사용법

### 기본 명령어

```bash
# 기본 변환 (자동 감지)
python main.py sample_data.json

# 출력 파일명 지정
python main.py sample_data.json -o result.csv

# 도움말 보기
python main.py --help
```

### 고급 변환 모드

```bash
# 고급 평면화 모드: 배열의 각 요소를 개별 필드로 분리
python main.py sample_data.json --flatten

# 전치 변환 모드: 특수 구조를 계층적 헤더로 변환
python main.py sample_data.json --transpose

# 자동 감지: 구조에 맞는 최적 모드 자동 선택 (권장)
python main.py sample_data.json
```

## 변환 모드

### 1. 기본 모드
일반적인 JSON 배열을 CSV로 변환합니다.

**입력:**
```json
[
  {"id": 1, "name": "김철수", "age": 25},
  {"id": 2, "name": "이영희", "age": 30}
]
```

**출력:**
```csv
id,name,age
1,김철수,25
2,이영희,30
```

### 2. 고급 평면화 모드 (`--flatten`)
중첩된 객체와 배열을 개별 필드로 분리합니다.

**입력:**
```json
[
  {
    "id": 1,
    "skills": ["Python", "JavaScript"],
    "address": {"city": "서울", "district": "강남구"}
  }
]
```

**출력:**
```csv
address.city,address.district,id,skills[0],skills[1]
서울,강남구,1,Python,JavaScript
```

### 3. 전치 변환 모드 (`--transpose`)
특수 구조의 배열들을 각 인덱스별로 행으로 변환합니다.

**입력:**
```json
[
  {
    "keyword": "수치분석",
    "data": {
      "months": ["2024-01", "2024-02", "2024-03"],
      "values": [100, 200, 150]
    }
  }
]
```

**출력:**
```csv
keyword,data,data
,months,values
수치분석,2024-01,100
,2024-02,200
,2024-03,150
```

## 특징

1. **자동 감지**: 특수 구조를 자동으로 인식하여 최적 변환 모드 선택
2. **필드 순서 유지**: 첫 번째 객체의 필드 순서대로 CSV 헤더 정렬
3. **3가지 변환 모드**: 기본, 고급 평면화, 전치 변환
4. **계층적 헤더**: 전치 모드에서 중첩 구조를 계층적으로 표현
5. **유연한 스키마**: 각 객체가 다른 필드를 가져도 자동 처리
6. **한글 완벽 지원**: UTF-8 인코딩으로 한글 데이터 처리
7. **상세한 오류 처리**: 명확한 오류 메시지와 예외 처리

## 테스트

포함된 샘플 데이터로 테스트해보세요:

```bash
# 기본 변환 테스트
python main.py sample_data.json

# 제품 데이터 테스트
python main.py sample_data.json

# 고급 평면화 테스트
python main.py sample_data.json --flatten

# 특수 구조 변환 테스트 (자동 감지)
python main.py sample_data.json

# 전치 변환 테스트 (수동 지정)
python main.py sample_data.json --transpose

# 대용량 데이터 성능 테스트
python main.py sample_data.json
```

## 설치 및 요구사항

### 필수 요구사항
- Python 3.11 이상 (Python 3.12 권장)
- 추가 의존성 없음 (표준 라이브러리만 사용)

### 설치

#### 1. Python 버전 관리 (pyenv 사용)
이 프로젝트는 Python 3.12에 최적화되어 있습니다. pyenv를 사용하면 자동으로 올바른 Python 버전이 설정됩니다.

```bash
# pyenv 설치 (macOS)
brew install pyenv

# Python 3.12 설치
pyenv install 3.12

# 프로젝트 클론
git clone <repository-url>
cd json-to-csv

# pyenv가 자동으로 Python 3.12를 활성화합니다 (.python-version 파일 참조)
python --version  # Python 3.12 출력 확인
```

#### 2. 기본 설치
```bash
# Git 클론
git clone <repository-url>
cd json-to-csv

# 실행 권한 부여 (선택사항)
chmod +x main.py

# 직접 실행
./main.py sample_data.json
```

### pyenv 설정 정보
- `.python-version` 파일이 포함되어 있어 프로젝트 디렉토리에서 자동으로 Python 3.12가 활성화됩니다
- pyenv가 설치되어 있다면 별도 설정 없이 최적의 Python 버전이 사용됩니다
- 수동으로 Python 버전을 변경하려면: `pyenv local 3.12`

## 사용 예시

### 단순 데이터 변환
```bash
python main.py sample_data.json -o data.csv
```

### 복잡한 중첩 데이터
```bash
python main.py sample_data.json --flatten -o flattened.csv
```

### 특수 구조(계층적 헤더) 데이터
```bash
python main.py sample_data.json -o transpose.csv
```

이 도구는 다양한 JSON 구조를 지능적으로 분석하여 가장 적절한 CSV 형태로 변환합니다.
