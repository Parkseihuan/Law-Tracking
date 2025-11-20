#!/usr/bin/env python3
"""
mcp-kr-legislation 라이브러리를 활용한 법령 관계 수집
"""

import os
import sys
import json
from pathlib import Path

# cffi 의존성 경로 추가
sys.path.insert(0, '/tmp/pymodules')

os.environ['LEGISLATION_API_KEY'] = 'psh@yi.ac.kr'

from mcp_kr_legislation.tools.law_tools import (
    search_law_system_diagram,
    get_law_system_diagram_detail,
    get_law_system_diagram_full
)


def test_law_system_diagram():
    """법령 체계도 API 테스트"""

    test_laws = ["사립학교법", "교육공무원법", "근로기준법", "교육기본법"]

    print("="*80)
    print("🔍 법령 체계도 API 테스트")
    print("="*80)

    for law_name in test_laws:
        print(f"\n📋 {law_name}")
        print("-" * 60)

        try:
            # 1. 체계도 검색
            result = search_law_system_diagram(query=law_name, display=5)
            print(f"\n검색 결과:\n{result.text[:500]}...")

            # 결과 파싱하여 MST ID 추출 시도
            if "MST" in result.text or "mst_id" in result.text.lower():
                print("\n✅ 체계도 발견!")
                # 여기서 MST ID를 추출하여 상세 정보 조회 가능
            else:
                print("\n⚠️  체계도 없음 또는 접근 불가")

        except Exception as e:
            print(f"❌ 오류: {e}")


def extract_relationships_from_diagram(diagram_data: dict) -> dict:
    """
    법령 체계도 데이터에서 관계 정보 추출

    Args:
        diagram_data: 체계도 API 응답 데이터

    Returns:
        관계 정보 딕셔너리
    """
    relationships = {
        "상위법령": [],
        "하위법령": [],
        "관련법령": []
    }

    # TODO: 실제 API 응답 구조에 맞게 파싱 로직 구현
    # 예시:
    # if "상위법" in diagram_data:
    #     for law in diagram_data["상위법"]:
    #         relationships["상위법령"].append({
    #             "법령명": law.get("name"),
    #             "법령일련번호": law.get("mst_id")
    #         })

    return relationships


if __name__ == "__main__":
    test_law_system_diagram()
