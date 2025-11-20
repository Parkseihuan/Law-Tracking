#!/usr/bin/env python3
"""
법령 관계 업데이트 스크립트
추적 중인 모든 법령의 체계도를 크롤링하여 관계 데이터를 업데이트
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from law_tracker import LawTracker
from law_hierarchy_scraper import LawHierarchyScraper
from law_hierarchy import LawHierarchy

load_dotenv()


def main():
    """메인 함수"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print("="*80)
    print("🔄 법령 관계 데이터 업데이트")
    print("="*80)

    # 1. LawTracker 초기화
    print("\n1️⃣  추적 중인 법령 로드...")
    tracker = LawTracker(api_key)
    tracked_laws = tracker.tracked_laws

    if not tracked_laws:
        print("❌ 추적 중인 법령이 없습니다.")
        print("   먼저 law_tracker.py로 법령을 추가해주세요.")
        return

    print(f"✅ {len(tracked_laws)}개의 법령을 추적 중입니다:")
    for i, law_name in enumerate(tracked_laws.keys(), 1):
        print(f"   {i}. {law_name}")

    # 2. 법령 체계도 크롤링
    print("\n2️⃣  법령 체계도 크롤링 시작...")
    scraper = LawHierarchyScraper()
    scraper.scrape_all_tracked_laws(tracked_laws)

    # 3. 크롤링 결과 확인
    print("\n3️⃣  크롤링 결과 확인...")
    relationships = scraper.get_all_relationships()

    if relationships:
        print(f"✅ {len(relationships)}개 법령의 관계 데이터 수집 완료")

        # 상세 정보 출력
        for law_name, data in relationships.items():
            print(f"\n📋 {law_name}")
            print(f"   상위법령: {len(data.get('상위법령', []))}개")
            print(f"   하위법령: {len(data.get('하위법령', []))}개")
            print(f"   관련법령: {len(data.get('관련법령', []))}개")

            # 법령명 출력
            for upper in data.get('상위법령', [])[:3]:  # 최대 3개만
                if isinstance(upper, dict):
                    print(f"      ↑ {upper.get('법령명', '이름없음')}")
            for lower in data.get('하위법령', [])[:3]:
                if isinstance(lower, dict):
                    print(f"      ↓ {lower.get('법령명', '이름없음')}")
    else:
        print("⚠️  크롤링된 데이터가 없습니다.")
        print("   웹사이트 접근이 차단되었을 수 있습니다.")

    # 4. 법령 체계도 시스템에 반영
    print("\n4️⃣  법령 체계도 시스템 업데이트...")
    hierarchy = LawHierarchy()
    hierarchy.reload_scraped_relationships()

    print("\n" + "="*80)
    print("✅ 법령 관계 데이터 업데이트 완료!")
    print("="*80)
    print("\n💡 웹 대시보드를 실행하여 업데이트된 법령 체계도를 확인하세요:")
    print("   python web_dashboard.py")


if __name__ == "__main__":
    main()
