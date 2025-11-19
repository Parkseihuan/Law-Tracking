#!/usr/bin/env python3
"""
파일에서 법령 목록을 읽어 일괄 추가
"""

import os
from law_tracker import LawTracker
from dotenv import load_dotenv

load_dotenv()


def read_law_list(filename="law_list.txt"):
    """파일에서 법령 목록 읽기"""
    laws = []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # 주석과 빈 줄 제거
                line = line.strip()
                if line and not line.startswith('#'):
                    laws.append(line)

        return laws

    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {filename}")
        return []


def add_laws_from_file():
    """파일에서 법령 목록을 읽어 추가"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print("="*80)
    print("📂 파일에서 법령 일괄 추가")
    print("="*80)

    # 법령 목록 읽기
    laws = read_law_list("law_list.txt")

    if not laws:
        print("\n❌ law_list.txt 파일에 법령이 없습니다.")
        print("💡 law_list.txt 파일을 열어서 추가할 법령을 입력하세요.")
        return

    print(f"\n📋 law_list.txt에서 읽은 법령 ({len(laws)}개):")
    print("-"*80)
    for i, law_name in enumerate(laws, 1):
        print(f"{i:2d}. {law_name}")
    print("-"*80)

    # 확인
    confirm = input("\n위 법령들을 모두 추가하시겠습니까? (y/n): ").strip().lower()

    if confirm != 'y':
        print("취소되었습니다.")
        return

    # 추가 시작
    tracker = LawTracker(api_key)

    print("\n🚀 법령 추가 시작...\n")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, law_name in enumerate(laws, 1):
        print(f"\n[{i}/{len(laws)}] {law_name}")

        # 이미 추적 중이면 건너뛰기
        if law_name in tracker.tracked_laws:
            print(f"   ⏭️  이미 추적 중 - 건너뛰기")
            skip_count += 1
            continue

        # 법령 추가
        try:
            success = tracker.add_law(law_name)
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            fail_count += 1

    # 결과 요약
    print("\n" + "="*80)
    print("📊 추가 결과")
    print("="*80)
    print(f"✅ 성공: {success_count}개")
    print(f"⏭️  건너뛰기: {skip_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📋 총 추적 법령: {len(tracker.tracked_laws)}개")

    # 최종 목록
    print("\n" + "="*80)
    print("✅ 작업 완료!")
    print("="*80)
    tracker.list_tracked_laws()


if __name__ == "__main__":
    add_laws_from_file()
