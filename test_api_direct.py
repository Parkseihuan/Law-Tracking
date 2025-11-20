#!/usr/bin/env python3
"""
국가법령정보센터 API 직접 호출 테스트
"""

import sys
sys.path.insert(0, '/tmp/pymodules')

import os
os.environ['LEGISLATION_API_KEY'] = 'psh@yi.ac.kr'

from mcp_kr_legislation.apis.client import LegislationClient
from mcp_kr_legislation.config import legislation_config


def test_legislation_api():
    """법제처 API 직접 테스트"""

    print("="*80)
    print("🔍 법제처 API 직접 호출 테스트")
    print("="*80)

    client = LegislationClient(config=legislation_config)

    # 테스트 1: 법령 체계도 검색 (lsStmd)
    print("\n1️⃣  법령 체계도 검색 API (lsStmd)")
    print("-" * 60)

    test_laws = ["사립학교법", "교육기본법"]

    for law_name in test_laws:
        print(f"\n📋 {law_name}")

        try:
            # legislation API 사용 (law API와 다름)
            result = client.legislation_api.make_request(
                endpoint="lsStmd",
                params={
                    "query": law_name,
                    "display": 5,
                    "type": "JSON"
                }
            )

            print(f"✅ 응답 타입: {type(result)}")
            print(f"응답 키: {result.keys() if isinstance(result, dict) else 'dict 아님'}")

            if isinstance(result, dict):
                if "error" in result:
                    print(f"❌ 에러: {result['error']}")
                else:
                    print(f"데이터 샘플: {str(result)[:500]}...")
            else:
                print(f"응답: {str(result)[:500]}...")

        except Exception as e:
            print(f"❌ 오류: {e}")

    # 테스트 2: 일반 법령 검색 (lawSearch) - 비교용
    print("\n\n2️⃣  일반 법령 검색 API (lawSearch) - 비교")
    print("-" * 60)

    try:
        result = client.search("law", {"query": "교육기본법"})
        print(f"✅ 응답 타입: {type(result)}")
        print(f"응답 키: {result.keys() if isinstance(result, dict) else 'dict 아님'}")

        if isinstance(result, dict) and "error" in result:
            print(f"❌ 에러: {result['error']}")
            print(f"상태 코드: {result.get('status_code')}")

    except Exception as e:
        print(f"❌ 오류: {e}")


if __name__ == "__main__":
    test_legislation_api()
