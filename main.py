#!/usr/bin/env python3
"""
JSON to CSV 변환 유틸리티

JSON 배열을 CSV 파일로 변환하는 고성능 Python 스크립트입니다.
다양한 변환 모드와 자동 감지 기능을 제공합니다.

주요 기능:
- 기본 변환: JSON 배열 → CSV
- 고급 평면화: 중첩 객체/배열을 개별 필드로 분리
- 전치 변환: 특수 구조를 계층적 헤더로 변환
- 자동 감지: 데이터 구조에 맞는 최적 모드 선택

Requirements: Python 3.11+
"""

import json
import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
import time

# 최소 Python 버전 확인
python_version = sys.version_info
if python_version < (3, 11):
    print(f"❌ 오류: Python {python_version.major}.{python_version.minor} 감지됨. 최소 요구사항: Python 3.11+")
    sys.exit(1)

def transpose_nested_arrays(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    중첩된 배열들을 전치하여 각 인덱스별로 행을 생성합니다.
    
    특수 구조를 처리할 때 사용됩니다.
    배열의 각 인덱스가 별도의 행이 되어 더 직관적인 CSV 구조를 만듭니다.
    
    Args:
        data: JSON 객체들의 리스트
        
    Returns:
        전치된 데이터의 리스트
    """
    if not data or not isinstance(data[0], dict):
        return data
    
    result = []
    
    for item in data:
        # 데이터를 단일 값과 배열로 분리
        single_values = {}
        array_groups = {}
        
        def extract_arrays(obj, prefix=""):
            """중첩된 객체에서 배열과 단일 값을 분리하는 내부 함수"""
            nonlocal single_values, array_groups
            
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # 중첩 객체는 재귀적으로 처리
                    extract_arrays(value, full_key)
                elif isinstance(value, list):
                    # 배열은 그룹별로 분류
                    group_name = prefix if prefix else "root"
                    if group_name not in array_groups:
                        array_groups[group_name] = {}
                    array_groups[group_name][key] = value
                else:
                    # 단일 값은 별도 저장
                    single_values[full_key] = value
        
        extract_arrays(item)
        
        # 모든 배열의 최대 길이 계산
        max_length = 0
        for group in array_groups.values():
            for arr in group.values():
                max_length = max(max_length, len(arr))
        
        if max_length == 0:
            # 배열이 없으면 원본 데이터 유지
            result.append(item)
            continue
        
        # 배열 길이만큼 행 생성
        for i in range(max_length):
            row = {}
            
            # 단일 값은 첫 번째 행에만 추가
            for key, value in single_values.items():
                row[key] = value if i == 0 else ""
            
            # 배열 값들을 해당 인덱스에 맞게 추가
            for group_name, arrays in array_groups.items():
                for array_name, array_values in arrays.items():
                    if group_name == "root":
                        field_name = array_name
                    else:
                        field_name = f"{group_name}.{array_name}"
                    
                    if i < len(array_values):
                        row[field_name] = array_values[i]
                    else:
                        row[field_name] = ""
            
            result.append(row)
    
    return result


def detect_transpose_structure(data: List[Dict[str, Any]]) -> bool:
    """
    전치 변환이 필요한 특수 구조를 자동으로 감지합니다.
    
    단일 객체 내에 중첩된 배열이 있는 경우 전치 변환이 유용합니다.
    
    Args:
        data: JSON 객체들의 리스트
        
    Returns:
        전치 변환 필요 여부
    """
    if not data or len(data) != 1:
        return False
    
    item = data[0]
    if not isinstance(item, dict):
        return False
    
    def has_nested_arrays(obj):
        """중첩된 객체 내부에 배열이 있는지 확인하는 내부 함수"""
        for value in obj.values():
            if isinstance(value, dict):
                # 중첩 객체 내부의 배열 확인
                for nested_value in value.values():
                    if isinstance(nested_value, list):
                        return True
                if has_nested_arrays(value):
                    return True
            elif isinstance(value, list):
                return True
        return False
    
    return has_nested_arrays(item)


def flatten_nested_data(obj: Any, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    중첩된 객체와 배열을 평면화합니다.
    
    배열의 각 요소는 [인덱스] 형태로 개별 필드가 됩니다.
    예: {"items": ["a", "b"]} → {"items[0]": "a", "items[1]": "b"}
    
    Args:
        obj: 평면화할 객체
        parent_key: 부모 키 (재귀 호출용)
        sep: 키 구분자
        
    Returns:
        평면화된 딕셔너리
    """
    items = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            items.extend(flatten_nested_data(value, new_key, sep).items())
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            new_key = f"{parent_key}[{i}]" if parent_key else f"[{i}]"
            if isinstance(value, (dict, list)):
                items.extend(flatten_nested_data(value, new_key, sep).items())
            else:
                items.append((new_key, value))
    else:
        items.append((parent_key, obj))
    
    return dict(items)


def extract_all_keys_advanced(json_data: List[Dict[str, Any]]) -> List[str]:
    """
    평면화된 데이터에서 모든 키를 추출합니다.
    
    중첩된 객체와 배열을 평면화한 후 키를 수집합니다.
    첫 번째 객체의 필드 순서를 우선으로 합니다.
    
    Args:
        json_data: JSON 객체들의 리스트
        
    Returns:
        정렬된 키 리스트
    """
    if not json_data:
        return []
    
    # 모든 객체를 평면화하여 키 수집
    all_keys: Set[str] = set()
    first_item_keys = []
    
    for i, item in enumerate(json_data):
        if isinstance(item, dict):
            flattened = flatten_nested_data(item)
            all_keys.update(flattened.keys())
            
            # 첫 번째 객체의 키 순서 저장
            if i == 0:
                first_item_keys = list(flattened.keys())
    
    # 첫 번째 객체 순서 우선, 나머지는 알파벳 순
    ordered_keys = first_item_keys.copy()
    remaining_keys = sorted(all_keys - set(first_item_keys))
    ordered_keys.extend(remaining_keys)
    
    return ordered_keys


def extract_all_keys(json_data: List[Dict[str, Any]]) -> List[str]:
    """
    기본 모드에서 모든 키를 추출합니다.
    
    중첩된 객체나 배열은 평면화하지 않고 그대로 둡니다.
    첫 번째 객체의 필드 순서를 우선으로 합니다.
    
    Args:
        json_data: JSON 객체들의 리스트
        
    Returns:
        정렬된 키 리스트
    """
    if not json_data:
        return []
    
    # 첫 번째 객체의 키 순서를 기준으로 시작
    first_item_keys = []
    if isinstance(json_data[0], dict):
        first_item_keys = list(json_data[0].keys())
    
    # 모든 객체에서 키 수집
    all_keys: Set[str] = set()
    for item in json_data:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    # 첫 번째 객체 순서 우선, 나머지는 알파벳 순
    ordered_keys = first_item_keys.copy()
    remaining_keys = sorted(all_keys - set(first_item_keys))
    ordered_keys.extend(remaining_keys)
    
    return ordered_keys


def flatten_value(value: Any) -> str:
    """
    중첩된 값을 CSV 필드용 문자열로 변환합니다.
    
    딕셔너리나 리스트는 JSON 문자열로 변환됩니다.
    
    Args:
        value: 변환할 값
        
    Returns:
        문자열로 변환된 값
    """
    if value is None:
        return ""
    elif isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    else:
        return str(value)


def json_to_csv(json_file_path: str, csv_file_path: str = None, flatten_arrays: bool = False, transpose: bool = False) -> None:
    """
    JSON 파일을 CSV 파일로 변환합니다.
    
    Args:
        json_file_path: 입력 JSON 파일 경로
        csv_file_path: 출력 CSV 파일 경로 (None이면 자동 생성)
        flatten_arrays: 고급 평면화 모드 활성화
        transpose: 전치 변환 모드 활성화
    """
    start_time = time.perf_counter()
    
    # 입력 파일 존재 확인
    input_path = Path(json_file_path)
    if not input_path.exists():
        raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
    
    # 출력 파일 경로 자동 생성
    if csv_file_path is None:
        if transpose:
            suffix = '_transposed.csv'
        elif flatten_arrays:
            suffix = '_flattened.csv'
        else:
            suffix = '.csv'
        csv_file_path = input_path.with_suffix(suffix)
    
    # JSON 데이터 읽기
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as e:
        raise ValueError(f"잘못된 JSON 형식입니다: {e}")
    except Exception as e:
        raise Exception(f"JSON 파일을 읽는 중 오류가 발생했습니다: {e}")
    
    # 데이터 유효성 검증
    if not isinstance(data, list):
        raise ValueError("JSON 데이터는 배열이어야 합니다.")
    
    if not data:
        print("경고: JSON 배열이 비어있습니다.")
        # 빈 CSV 파일 생성
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            pass
        return
    
    # 자동 감지: 전치 변환 필요 여부 확인
    auto_transpose = detect_transpose_structure(data) and not flatten_arrays and not transpose
    if auto_transpose:
        transpose = True
        print(f"🔍 자동 감지: 전치 변환이 필요한 구조를 발견했습니다.")
    
    # 변환 모드에 따른 데이터 처리
    if transpose:
        print(f"🔄 전치 변환 모드: 중첩된 배열들을 각 인덱스별로 행으로 변환")
        processed_data = transpose_nested_arrays(data)
        headers = extract_all_keys(processed_data)
    elif flatten_arrays:
        print(f"🔄 고급 평면화 모드: 중첩 객체와 배열을 개별 필드로 분리")
        processed_data = data
        headers = extract_all_keys_advanced(data)
    else:
        processed_data = data
        headers = extract_all_keys(data)
    
    if not headers:
        print("경고: JSON 객체에서 키를 찾을 수 없습니다.")
        return
    
    # CSV 파일 작성
    try:
        if transpose:
            # 전치 모드: 계층적 헤더 사용
            write_hierarchical_csv(csv_file_path, headers, processed_data)
        else:
            # 기본/평면화 모드: 일반 CSV 사용
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers)
                
                # 헤더 작성
                writer.writeheader()
                
                # 데이터 행 작성
                for item in processed_data:
                    if isinstance(item, dict):
                        if flatten_arrays:
                            # 고급 평면화 처리
                            flattened_item = flatten_nested_data(item)
                            row = {key: str(flattened_item.get(key, "")) for key in headers}
                        else:
                            # 기본 모드 처리
                            row = {key: flatten_value(item.get(key)) for key in headers}
                        writer.writerow(row)
                    else:
                        print(f"경고: 객체가 아닌 항목을 건너뜁니다: {item}")
        
        # 처리 완료 메시지
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        if transpose:
            mode = "전치 변환"
        elif flatten_arrays:
            mode = "고급 평면화"
        else:
            mode = "기본"
        
        print(f"✅ 변환 완료: {csv_file_path}")
        print(f"   - 총 {len(processed_data)}개의 행 생성")
        print(f"   - {len(headers)}개의 열: {', '.join(headers[:5])}" + 
              (f", ..." if len(headers) > 5 else ""))
        print(f"   - 처리 모드: {mode}")
        print(f"   - 처리 시간: {processing_time:.3f}초")
        
    except Exception as e:
        raise Exception(f"CSV 파일을 작성하는 중 오류가 발생했습니다: {e}")


def create_hierarchical_headers(headers: List[str]) -> Tuple[List[str], List[str]]:
    """
    점으로 구분된 헤더를 계층적 구조로 변환합니다.
    
    예: ["name", "user.age", "user.city"] → (["name", "user", "user"], ["", "age", "city"])
    
    Args:
        headers: 점으로 구분된 헤더 리스트
        
    Returns:
        (상위 헤더, 하위 헤더) 튜플
    """
    top_headers = []
    sub_headers = []
    
    for header in headers:
        if '.' in header:
            parts = header.split('.', 1)
            top_headers.append(parts[0])
            sub_headers.append(parts[1])
        else:
            top_headers.append(header)
            sub_headers.append("")
    
    return top_headers, sub_headers


def write_hierarchical_csv(csv_file_path: str, headers: List[str], data: List[Dict[str, Any]]) -> None:
    """
    계층적 헤더를 가진 CSV 파일을 작성합니다.
    
    전치 변환 모드에서 사용되며, 상위/하위 헤더를 두 줄로 나누어 작성합니다.
    
    Args:
        csv_file_path: 출력 CSV 파일 경로
        headers: 헤더 리스트
        data: 데이터 리스트
    """
    top_headers, sub_headers = create_hierarchical_headers(headers)
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # 상위/하위 헤더 작성
        writer.writerow(top_headers)
        writer.writerow(sub_headers)
        
        # 데이터 행 작성
        for item in data:
            row = []
            for header in headers:
                value = item.get(header, "")
                row.append(str(value))
            writer.writerow(row)


def main():
    """
    명령행 인터페이스를 통한 메인 실행 함수
    """
    parser = argparse.ArgumentParser(
        description="JSON 배열을 CSV 파일로 변환합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py data.json
  python main.py data.json -o output.csv
  python main.py data.json --output result.csv
  python main.py data.json --flatten  # 고급 평면화 모드
  python main.py data.json --transpose  # 전치 변환 모드
        """
    )
    
    parser.add_argument(
        'input_file',
        help='변환할 JSON 파일 경로'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='출력 CSV 파일 경로 (생략하면 입력 파일명.csv로 생성)'
    )
    
    parser.add_argument(
        '--flatten', 
        action='store_true',
        help='고급 평면화 모드: 중첩된 객체와 배열을 개별 필드로 분리'
    )
    
    parser.add_argument(
        '--transpose', 
        action='store_true',
        help='전치 변환 모드: 중첩된 배열들을 각 인덱스별로 행으로 변환'
    )
    
    args = parser.parse_args()
    
    # 상호 배타적 옵션 검증
    if args.flatten and args.transpose:
        print("❌ 오류: --flatten과 --transpose 옵션은 동시에 사용할 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    
    try:
        json_to_csv(args.input_file, args.output, args.flatten, args.transpose)
    except Exception as e:
        print(f"❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
