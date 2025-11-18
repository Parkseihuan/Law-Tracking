#!/usr/bin/env python3
"""
법령 추적 시스템 - 알림 기능 포함
"""

import os
from law_tracker import LawTracker
from notification_system import NotificationSystem
from dotenv import load_dotenv

load_dotenv()


def main():
    """메인 함수 - 알림 기능 포함"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print("="*80)
    print("🏛️  법령 추적 시스템 (알림 기능 포함)")
    print("="*80)
    print(f"API 키: {api_key}\n")

    # 추적기 생성
    tracker = LawTracker(api_key)

    # 알림 시스템 초기화
    notifier = NotificationSystem()

    # 추적 대상 법령이 없으면 추가
    if not tracker.tracked_laws:
        print("📋 추적 대상 법령을 추가합니다...\n")
        tracker.add_law("사립학교법")
        tracker.add_law("고등교육법")
    else:
        print(f"📋 현재 {len(tracker.tracked_laws)}개 법령 추적 중\n")

    # 변경사항 확인
    updates = tracker.check_updates()

    # 알림 발송
    if updates:
        print("\n" + "="*80)
        print("📬 알림 발송")
        print("="*80)
        notifier.notify_law_changes(updates)

        print(f"\n✅ {len(updates)}개 법령의 변경사항이 확인되었습니다!")
    else:
        print("\n✅ 모든 법령이 최신 상태입니다.")

    # 추적 목록 요약
    print("\n" + "="*80)
    print("📊 추적 현황")
    print("="*80)
    tracker.list_tracked_laws()


if __name__ == "__main__":
    main()
