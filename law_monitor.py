#!/usr/bin/env python3
"""
법령 개정 모니터링 시스템 - 프로토타입
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()


class LawMonitor:
    """법령 모니터링 클래스"""

    def __init__(self, api_key: str, data_dir: str = "data"):
        self.api_key = api_key
        self.base_url = "http://www.law.go.kr/DRF"
        self.data_dir = Path(data_dir)

        # 디렉토리 생성
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "cache").mkdir(exist_ok=True)
        (self.data_dir / "history").mkdir(exist_ok=True)

        # 감시 대상 법령 목록
        self.watched_laws_file = self.data_dir / "watched_laws.json"
        self.watched_laws = self._load_watched_laws()

    def _load_watched_laws(self) -> Dict:
        """감시 대상 법령 목록 로드"""
        if self.watched_laws_file.exists():
            with open(self.watched_laws_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_watched_laws(self):
        """감시 대상 법령 목록 저장"""
        with open(self.watched_laws_file, 'w', encoding='utf-8') as f:
            json.dump(self.watched_laws, f, ensure_ascii=False, indent=2)

    def add_law(self, law_name: str, law_mst_seq: Optional[str] = None):
        """감시 대상 법령 추가"""
        # 법령 검색
        if not law_mst_seq:
            law_info = self._search_law(law_name)
            if not law_info:
                print(f"❌ 법령을 찾을 수 없습니다: {law_name}")
                return False

            law_mst_seq = law_info.get('mst')
            law_name = law_info.get('name', law_name)

        # 감시 목록에 추가
        self.watched_laws[law_name] = {
            "mst": law_mst_seq,
            "added_date": datetime.now().isoformat(),
            "last_checked": None,
            "last_modified": None,
            "hash": None
        }

        self._save_watched_laws()
        print(f"✅ 감시 대상 추가: {law_name} (MST: {law_mst_seq})")
        return True

    def remove_law(self, law_name: str):
        """감시 대상 법령 제거"""
        if law_name in self.watched_laws:
            del self.watched_laws[law_name]
            self._save_watched_laws()
            print(f"✅ 감시 대상 제거: {law_name}")
            return True
        else:
            print(f"❌ 감시 대상에 없습니다: {law_name}")
            return False

    def _search_law(self, law_name: str) -> Optional[Dict]:
        """법령 검색 (API 호출)"""
        params = {
            'target': 'law',
            'query': law_name,
            'display': 1,
            'type': 'XML',
            'OC': self.api_key
        }

        try:
            url = f"{self.base_url}/lawSearch.do"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                # XML 파싱 로직 (간소화)
                # 실제로는 ElementTree로 파싱
                return {"name": law_name, "mst": "example_mst_seq"}
            else:
                return None

        except Exception as e:
            print(f"❌ API 오류: {e}")
            return None

    def _get_law_detail(self, law_mst_seq: str) -> Optional[Dict]:
        """법령 상세 정보 조회"""
        params = {
            'target': 'law',
            'MST': law_mst_seq,
            'type': 'XML',
            'OC': self.api_key
        }

        try:
            url = f"{self.base_url}/lawService.do"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return {
                    "content": response.text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return None

        except Exception as e:
            print(f"❌ API 오류: {e}")
            return None

    def _calculate_hash(self, content: str) -> str:
        """내용의 해시값 계산"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def check_updates(self) -> List[Dict]:
        """모든 감시 대상 법령의 업데이트 확인"""
        updates = []

        for law_name, info in self.watched_laws.items():
            print(f"\n🔍 확인 중: {law_name}")

            # 법령 상세 정보 조회
            detail = self._get_law_detail(info['mst'])

            if not detail:
                print(f"   ⚠️  조회 실패")
                continue

            # 해시값 계산
            current_hash = self._calculate_hash(detail['content'])

            # 이전 해시와 비교
            if info['hash'] and info['hash'] != current_hash:
                print(f"   🔔 변경 감지!")
                updates.append({
                    "law_name": law_name,
                    "mst": info['mst'],
                    "old_hash": info['hash'],
                    "new_hash": current_hash,
                    "timestamp": detail['timestamp']
                })

                # 변경 이력 저장
                self._save_history(law_name, detail)

            else:
                print(f"   ✅ 변경 없음")

            # 상태 업데이트
            info['last_checked'] = datetime.now().isoformat()
            info['hash'] = current_hash

        self._save_watched_laws()
        return updates

    def _save_history(self, law_name: str, detail: Dict):
        """법령 변경 이력 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / "history" / f"{law_name}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detail, f, ensure_ascii=False, indent=2)

        print(f"   💾 이력 저장: {filename}")

    def list_watched_laws(self):
        """감시 중인 법령 목록 출력"""
        if not self.watched_laws:
            print("📋 감시 중인 법령이 없습니다.")
            return

        print("\n📋 감시 중인 법령 목록:")
        print("=" * 80)

        for law_name, info in self.watched_laws.items():
            print(f"\n법령명: {law_name}")
            print(f"  - MST: {info['mst']}")
            print(f"  - 추가일: {info['added_date']}")
            print(f"  - 마지막 확인: {info['last_checked'] or '없음'}")
            print(f"  - 해시: {info['hash'][:16] if info['hash'] else '없음'}...")

        print("=" * 80)

    def generate_comparison_report(self, law_name: str, old_version: str, new_version: str):
        """신구대조표 생성 (간소화 버전)"""
        print(f"\n📊 신구대조표 생성: {law_name}")
        print("=" * 80)

        # 실제로는 difflib를 사용하여 상세 비교
        import difflib

        diff = difflib.unified_diff(
            old_version.splitlines(keepends=True),
            new_version.splitlines(keepends=True),
            fromfile='개정 전',
            tofile='개정 후',
            lineterm=''
        )

        report_file = self.data_dir / f"{law_name}_비교_{datetime.now().strftime('%Y%m%d')}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(''.join(diff))

        print(f"✅ 신구대조표 저장: {report_file}")
        return report_file


def main():
    """메인 함수"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다.")
        return

    monitor = LawMonitor(api_key)

    # 사용 예시
    print("="*80)
    print("🏛️  법령 개정 모니터링 시스템")
    print("="*80)

    # 예제: 법령 추가
    print("\n1️⃣  감시 대상 법령 추가")
    monitor.add_law("사립학교법")
    monitor.add_law("고등교육법")

    # 감시 목록 확인
    print("\n2️⃣  감시 목록 확인")
    monitor.list_watched_laws()

    # 업데이트 확인 (실제로는 스케줄러로 주기적 실행)
    print("\n3️⃣  업데이트 확인")
    updates = monitor.check_updates()

    if updates:
        print(f"\n🔔 {len(updates)}개의 법령이 변경되었습니다!")
        for update in updates:
            print(f"   - {update['law_name']}")
    else:
        print("\n✅ 모든 법령이 최신 상태입니다.")


if __name__ == "__main__":
    main()
