#!/usr/bin/env python3
"""
간단한 API 테스트 - 다양한 방법 시도
"""

import requests
from urllib.parse import urlencode

def test_basic_access():
    """기본 접근 테스트"""
    print("="*60)
    print("🔍 국가법령정보센터 API 기본 접근 테스트")
    print("="*60)

    # 테스트 URL들
    test_cases = [
        {
            "name": "법제처 DRF - API 키 없이",
            "url": "http://www.law.go.kr/DRF/lawSearch.do",
            "params": {"target": "law", "query": "사립학교법", "display": 1, "type": "XML"}
        },
        {
            "name": "법제처 DRF - OC 파라미터",
            "url": "http://www.law.go.kr/DRF/lawSearch.do",
            "params": {"target": "law", "query": "사립학교법", "display": 1, "type": "XML", "OC": "psh"}
        },
        {
            "name": "법제처 LSW 접근",
            "url": "http://www.law.go.kr/LSW/lsInfoP.do",
            "params": {"lsiSeq": "61603"}  # 사립학교법 예시
        },
        {
            "name": "공공데이터포털 - serviceKey",
            "url": "http://apis.data.go.kr/1170000/law/lawSearch.do",
            "params": {"target": "law", "query": "사립학교법", "display": 1, "type": "XML", "serviceKey": "psh"}
        },
        {
            "name": "법령정보 RSS",
            "url": "http://www.law.go.kr/DRF/rss.do",
            "params": {"target": "law", "query": "사립학교법"}
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}] {test['name']}")
        print(f"URL: {test['url']}")
        print(f"Params: {test['params']}")

        try:
            response = requests.get(test['url'], params=test['params'], timeout=10)
            print(f"상태 코드: {response.status_code}")

            if response.status_code == 200:
                print("✅ 성공!")
                content = response.text[:500]
                print(f"응답 내용 (처음 500자):\n{content}\n")

                # XML 헤더 확인
                if "<?xml" in content:
                    print("   🎯 XML 응답 확인됨")
                if "error" in content.lower():
                    print("   ⚠️  에러 메시지 포함")
            else:
                print(f"❌ 실패 - 상태 코드: {response.status_code}")
                print(f"응답: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 예외 발생: {str(e)[:100]}")

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)

def check_api_documentation():
    """API 문서 접근 가능 여부 확인"""
    print("\n\n" + "="*60)
    print("📚 API 문서 접근 테스트")
    print("="*60)

    doc_urls = [
        "http://www.law.go.kr",
        "http://open.law.go.kr",
        "https://www.law.go.kr/DRF",
    ]

    for url in doc_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"\n{url}")
            print(f"   상태: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ 접근 가능")
        except Exception as e:
            print(f"\n{url}")
            print(f"   ❌ 접근 불가: {str(e)[:50]}")

if __name__ == "__main__":
    test_basic_access()
    check_api_documentation()
