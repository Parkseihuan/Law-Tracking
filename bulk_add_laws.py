#!/usr/bin/env python3
"""
법령 일괄 추가 도구
"""

import os
from law_tracker import LawTracker
from dotenv import load_dotenv

load_dotenv()


def bulk_add_laws():
    """여러 법령을 한꺼번에 추가"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print("="*80)
    print("📚 법령 일괄 추가 도구")
    print("="*80)

    tracker = LawTracker(api_key)

    # 추가할 법령 목록
    laws_to_add = [
        "사립학교법",
        "고등교육법",
        "교육기본법",
        "초중등교육법",
        "유아교육법",
        "교원지위법",
        "학교폭력예방법",
        "학교보건법",
        "교육공무원법",
        "사립학교교직원 연금법",
    ]

    print(f"\n📋 추가할 법령 목록 ({len(laws_to_add)}개):")
    print("-"*80)
    for i, law_name in enumerate(laws_to_add, 1):
        status = "✅ 이미 추적 중" if law_name in tracker.tracked_laws else "⏳ 추가 예정"
        print(f"{i:2d}. {law_name:30s} {status}")
    print("-"*80)

    # 사용자 확인
    print("\n위 법령들을 모두 추가하시겠습니까?")
    print("선택:")
    print("  1) 모두 추가")
    print("  2) 선택해서 추가")
    print("  3) 취소")

    choice = input("\n번호를 입력하세요 (1/2/3): ").strip()

    if choice == '1':
        # 모두 추가
        add_all_laws(tracker, laws_to_add)

    elif choice == '2':
        # 선택해서 추가
        select_and_add(tracker, laws_to_add)

    elif choice == '3':
        print("\n취소되었습니다.")
        return

    else:
        print("\n❌ 잘못된 선택입니다.")
        return

    # 최종 결과 출력
    print("\n" + "="*80)
    print("✅ 작업 완료!")
    print("="*80)
    tracker.list_tracked_laws()


def add_all_laws(tracker, laws):
    """모든 법령 추가"""
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


def select_and_add(tracker, laws):
    """선택해서 추가"""
    print("\n추가할 법령의 번호를 입력하세요 (쉼표로 구분, 예: 1,3,5)")
    print("또는 범위로 입력 (예: 1-5)")

    selection = input("\n선택: ").strip()

    # 선택 파싱
    selected_indices = parse_selection(selection, len(laws))

    if not selected_indices:
        print("❌ 잘못된 입력입니다.")
        return

    # 선택된 법령 추가
    selected_laws = [laws[i-1] for i in selected_indices]

    print(f"\n선택된 법령 ({len(selected_laws)}개):")
    for law in selected_laws:
        print(f"  - {law}")

    confirm = input("\n추가하시겠습니까? (y/n): ").strip().lower()

    if confirm == 'y':
        add_all_laws(tracker, selected_laws)
    else:
        print("취소되었습니다.")


def parse_selection(selection, max_num):
    """선택 입력 파싱"""
    indices = set()

    try:
        for part in selection.split(','):
            part = part.strip()

            if '-' in part:
                # 범위 (예: 1-5)
                start, end = map(int, part.split('-'))
                indices.update(range(start, end + 1))
            else:
                # 단일 번호
                indices.add(int(part))

        # 유효한 범위 확인
        valid_indices = [i for i in indices if 1 <= i <= max_num]
        return sorted(valid_indices)

    except:
        return []


if __name__ == "__main__":
    bulk_add_laws()
