#!/usr/bin/env python3
"""
대용량 JSON 테스트 데이터 생성기
"""

import json
import random
from datetime import datetime, timedelta

def generate_large_dataset(size: int = 5000) -> list:
    """대용량 JSON 데이터셋 생성"""
    
    departments = ['개발', '마케팅', '영업', '디자인', '기획', 'HR', '재무', '법무']
    cities = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '수원']
    districts = ['강남구', '서초구', '송파구', '마포구', '영등포구', '종로구', '중구', '용산구']
    skills = ['Python', 'JavaScript', 'Java', 'React', 'Node.js', 'Docker', 'AWS', 'Git', 'SQL', 'MongoDB']
    project_statuses = ['진행중', '완료', '보류', '계획', '취소']
    ratings = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D']
    
    dataset = []
    
    for i in range(size):
        # 랜덤 스킬 선택 (1-5개)
        user_skills = random.sample(skills, random.randint(1, 5))
        
        # 랜덤 프로젝트 생성 (1-4개)
        projects = []
        for j in range(random.randint(1, 4)):
            projects.append({
                "name": f"프로젝트{j + 1}_{i + 1}",
                "status": random.choice(project_statuses),
                "budget": random.randint(5000000, 50000000),
                "start_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
                "priority": random.choice(['높음', '보통', '낮음'])
            })
        
        user = {
            "id": i + 1,
            "user_id": f"user_{i + 1:05d}",
            "name": f"사용자{i + 1}",
            "email": f"user{i + 1}@example.com",
            "age": random.randint(22, 65),
            "department": random.choice(departments),
            "position": random.choice(['주니어', '시니어', '리드', '매니저', '디렉터']),
            "salary": random.randint(30000000, 100000000),
            "is_active": random.choice([True, False]),
            "skills": user_skills,
            "certifications": random.sample(['AWS', 'GCP', 'Azure', 'PMP', 'CISSP'], random.randint(0, 3)),
            "address": {
                "city": random.choice(cities),
                "district": random.choice(districts),
                "zipcode": f"{random.randint(10000, 99999)}",
                "detail": f"{random.randint(1, 999)}동 {random.randint(1, 50)}호"
            },
            "joined_date": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d"),
            "last_login": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
            "projects": projects,
            "performance": {
                "score": random.randint(60, 100),
                "rating": random.choice(ratings),
                "reviews": random.randint(1, 20),
                "goals_achieved": random.randint(0, 10),
                "training_hours": random.randint(10, 100)
            },
            "contact": {
                "phone": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "emergency_contact": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "slack_id": f"@user{i + 1}"
            },
            "preferences": {
                "theme": random.choice(['dark', 'light', 'auto']),
                "language": random.choice(['ko', 'en', 'ja']),
                "notifications": {
                    "email": random.choice([True, False]),
                    "sms": random.choice([True, False]),
                    "push": random.choice([True, False])
                }
            }
        }
        
        dataset.append(user)
    
    return dataset

if __name__ == "__main__":
    print("대용량 JSON 데이터셋 생성 중...")
    
    # 5000개 레코드 생성
    data = generate_large_dataset(5000)
    
    # JSON 파일로 저장
    with open('large_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 생성 완료: {len(data)}개의 레코드가 포함된 large_dataset.json 파일 생성")
    print(f"   - 파일 크기: 약 {len(json.dumps(data, ensure_ascii=False)) / 1024 / 1024:.1f}MB")
