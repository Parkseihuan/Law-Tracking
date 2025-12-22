#!/usr/bin/env python3
"""
법령 추적 시스템 - 실제 작동하는 API 기반
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import requests
from dotenv import load_dotenv
from comparison_generator import LawComparisonGenerator
from db_manager import DatabaseManager

class LawTracker:
    """법령 추적 클래스"""

    def __init__(self, api_key: str, data_dir: str = "data", use_mongodb: bool = True):
        self.api_key = api_key
        self.base_url = "http://www.law.go.kr/DRF"
        self.data_dir = Path(data_dir)

        # 디렉토리 생성 (fallback용)
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "cache").mkdir(exist_ok=True)
        (self.data_dir / "history").mkdir(exist_ok=True)
        (self.data_dir / "snapshots").mkdir(exist_ok=True)
        (self.data_dir / "diffs").mkdir(exist_ok=True)

        # MongoDB 초기화
        self.db = None
        if use_mongodb:
            try:
                self.db = DatabaseManager()
                if self.db.is_connected():
                    print("✅ Using MongoDB for data storage")
                else:
                    print("⚠️ MongoDB not available, using local file storage")
                    self.db = None
            except Exception as e:
                print(f"⚠️ MongoDB initialization failed: {e}, using local file storage")
                self.db = None

        # 추적 대상 법령 목록
        self.tracked_laws_file = self.data_dir / "tracked_laws.json"
        self.tracked_laws = self._load_tracked_laws()
        
        # 비교 생성기 초기화
        self.comparator = LawComparisonGenerator()

    def _load_tracked_laws(self) -> Dict:
        """추적 대상 법령 목록 로드 (MongoDB 우선, fallback to file)"""
        if self.db and self.db.is_connected():
            return self.db.get_all_tracked_laws()
        
        # Fallback to local file
        if self.tracked_laws_file.exists():
            with open(self.tracked_laws_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_tracked_laws(self):
        """추적 대상 법령 목록 저장 (MongoDB 우선, fallback to file)"""
        if self.db and self.db.is_connected():
            self.db.save_all_tracked_laws(self.tracked_laws)
        else:
            # Fallback to local file
            with open(self.tracked_laws_file, 'w', encoding='utf-8') as f:
                json.dump(self.tracked_laws, f, ensure_ascii=False, indent=2)


    def _xml_to_dict(self, element) -> Dict:
        """XML 요소를 딕셔너리로 변환"""
        result = {}

        # 속성 추가
        if element.attrib:
            result['@attributes'] = element.attrib

        # 텍스트 내용
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()

        # 자식 요소 처리
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result if result else element.text

    def search_law(self, law_name: str) -> Optional[Dict]:
        """법령 검색"""
        params = {
            'target': 'law',
            'query': law_name,
            'display': 5,
            'type': 'XML',
            'OC': self.api_key
        }

        try:
            url = f"{self.base_url}/lawSearch.do"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                root = ET.fromstring(response.text)
                result = self._xml_to_dict(root)
                return result
            else:
                print(f"❌ 검색 실패: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 오류: {e}")
            return None

    def get_law_detail(self, law_mst_seq: str) -> Optional[Dict]:
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
                root = ET.fromstring(response.text)
                result = self._xml_to_dict(root)
                return result
            else:
                return None

        except Exception as e:
            print(f"❌ 오류: {e}")
            return None

    def add_law(self, law_name: str):
        """추적 대상 법령 추가"""
        print(f"\n🔍 법령 검색 중: {law_name}")

        # 법령 검색
        search_result = self.search_law(law_name)
        if not search_result or 'law' not in search_result:
            print(f"❌ 법령을 찾을 수 없습니다: {law_name}")
            return False

        # 첫 번째 검색 결과 사용
        laws = search_result['law']
        if isinstance(laws, list):
            law = laws[0]
        else:
            law = laws

        law_mst_seq = law.get('법령일련번호')
        law_name_full = law.get('법령명한글', law_name)
        law_id = law.get('법령ID')

        print(f"✅ 발견: {law_name_full}")
        print(f"   법령일련번호: {law_mst_seq}")
        print(f"   법령ID: {law_id}")
        print(f"   공포일자: {law.get('공포일자')}")
        print(f"   시행일자: {law.get('시행일자')}")

        # 상세 정보 조회
        detail = self.get_law_detail(law_mst_seq)
        if detail:
            # 초기 스냅샷 저장
            self._save_snapshot(law_name_full, law_mst_seq, detail)

        # 추적 목록에 추가
        self.tracked_laws[law_name_full] = {
            "법령일련번호": law_mst_seq,
            "법령ID": law_id,
            "공포일자": law.get('공포일자'),
            "시행일자": law.get('시행일자'),
            "추가일시": datetime.now().isoformat(),
            "마지막확인": None,
            "마지막공포일자": law.get('공포일자'),
            "변경횟수": 0
        }

        self._save_tracked_laws()
        print(f"✅ 추적 목록에 추가됨: {law_name_full}")
        return True

    def remove_law(self, law_name: str):
        """추적 대상 법령 제거"""
        if law_name in self.tracked_laws:
            del self.tracked_laws[law_name]
            self._save_tracked_laws()
            print(f"✅ 추적 목록에서 제거: {law_name}")
            return True
        else:
            print(f"❌ 추적 중이지 않은 법령: {law_name}")
            return False

    def _save_snapshot(self, law_name: str, law_mst_seq: str, detail: Dict):
        """법령 스냅샷 저장 (MongoDB 우선, fallback to file)"""
        if self.db and self.db.is_connected():
            snapshot_id = self.db.save_snapshot(law_name, law_mst_seq, detail)
            if snapshot_id:
                return snapshot_id
        
        # Fallback to local file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / "snapshots" / f"{law_name}_{law_mst_seq}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "법령명": law_name,
                "법령일련번호": law_mst_seq,
                "저장일시": datetime.now().isoformat(),
                "상세정보": detail
            }, f, ensure_ascii=False, indent=2)

        return filename

    def _get_latest_snapshot(self, law_name: str) -> Optional[Dict]:
        """가장 최근 스냅샷 로드 (MongoDB 우선, fallback to file)"""
        if self.db and self.db.is_connected():
            snapshot = self.db.get_latest_snapshot(law_name)
            if snapshot:
                return snapshot
        
        # Fallback to local file
        snapshots = sorted(list((self.data_dir / "snapshots").glob(f"{law_name}_*.json")), reverse=True)
        if snapshots:
            try:
                with open(snapshots[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 스냅샷 로드 실패: {e}")
        return None

    def _extract_law_content(self, detail: Dict) -> str:
        """법령 상세 정보에서 조문 내용 추출"""
        content = []
        
        # 기본 정보
        if '기본정보' in detail:
            info = detail['기본정보']
            content.append(f"법령명: {info.get('법령명_한글', '')}")
            content.append(f"공포일자: {info.get('공포일자', '')}")
            content.append(f"시행일자: {info.get('시행일자', '')}")
            content.append("")

        # 조문 내용
        if '조문' in detail:
            articles = detail['조문']
            if isinstance(articles, dict): # 단일 조문
                articles = [articles]
            
            if isinstance(articles, list):
                for article in articles:
                    if '조문단위' in article: # 조문단위가 있는 경우 (조, 항, 호 등)
                        # 조문 내용 구성
                        article_text = f"{article.get('조문번호', '')} {article.get('조문제목', '')}".strip()
                        if '조문내용' in article:
                            article_text += f"\n{article['조문내용']}"
                        content.append(article_text)
                        
                        # 항 처리
                        if '항' in article:
                            hangs = article['항']
                            if isinstance(hangs, dict): hangs = [hangs]
                            for hang in hangs:
                                if '항내용' in hang:
                                    content.append(f"  {hang['항내용']}")
                                    
                                    # 호 처리
                                    if '호' in hang:
                                        hos = hang['호']
                                        if isinstance(hos, dict): hos = [hos]
                                        for ho in hos:
                                            if '호내용' in ho:
                                                content.append(f"    {ho['호내용']}")
        
        return "\n".join(content)

    def check_updates(self) -> List[Dict]:
        """모든 추적 대상 법령의 업데이트 확인"""
        updates = []

        print("\n" + "="*80)
        print("🔍 법령 변경사항 확인 시작")
        print("="*80)

        for law_name, info in self.tracked_laws.items():
            print(f"\n📋 확인 중: {law_name}")
            print(f"   이전 공포일자: {info['마지막공포일자']}")

            # 현재 법령 정보 검색
            search_result = self.search_law(law_name)

            if not search_result or 'law' not in search_result:
                print(f"   ⚠️  조회 실패")
                continue

            laws = search_result['law']
            current_law = laws[0] if isinstance(laws, list) else laws

            current_pub_date = current_law.get('공포일자')
            current_mst_seq = current_law.get('법령일련번호')

            # 공포일자 비교
            if info['마지막공포일자'] != current_pub_date:
                print(f"   🔔 변경 감지!")
                print(f"   새 공포일자: {current_pub_date}")
                print(f"   새 법령일련번호: {current_mst_seq}")

                diff_file = None
                
                # 이전 스냅샷 로드 및 비교
                prev_snapshot = self._get_latest_snapshot(law_name)
                
                # 상세 정보 조회 및 저장
                detail = self.get_law_detail(current_mst_seq)
                if detail:
                    snapshot_file = self._save_snapshot(law_name, current_mst_seq, detail)
                    print(f"   💾 스냅샷 저장: {snapshot_file.name}")
                    
                    # 신구대조표 생성
                    if prev_snapshot and '상세정보' in prev_snapshot:
                        try:
                            old_content = self._extract_law_content(prev_snapshot['상세정보'])
                            new_content = self._extract_law_content(detail)
                            
                            # HTML 비교 생성
                            diff_filename = f"{law_name}_{current_pub_date}_diff.html"
                            diff_path = self.data_dir / "diffs" / diff_filename
                            
                            # Generate diff HTML
                            self.comparator.generate_side_by_side_comparison(
                                old_content, 
                                new_content, 
                                law_name, 
                                str(diff_path)
                            )
                            
                            # Save to MongoDB if available
                            if self.db and self.db.is_connected():
                                try:
                                    with open(diff_path, 'r', encoding='utf-8') as f:
                                        diff_content = f.read()
                                    self.db.save_diff(diff_filename, diff_content)
                                except Exception as e:
                                    print(f"   ⚠️ MongoDB diff 저장 실패: {e}")
                            
                            diff_file = diff_filename
                            print(f"   📊 신구대조표 생성: {diff_file}")
                        except Exception as e:
                            print(f"   ⚠️ 신구대조표 생성 실패: {e}")

                update_record = {
                    "법령명": law_name,
                    "이전공포일자": info['마지막공포일자'],
                    "현재공포일자": current_pub_date,
                    "이전법령일련번호": info['법령일련번호'],
                    "현재법령일련번호": current_mst_seq,
                    "확인일시": datetime.now().isoformat(),
                    "신구대조표": diff_file
                }
                updates.append(update_record)

                # 정보 업데이트
                info['법령일련번호'] = current_mst_seq
                info['마지막공포일자'] = current_pub_date
                info['공포일자'] = current_pub_date
                info['시행일자'] = current_law.get('시행일자')
                info['변경횟수'] = info.get('변경횟수', 0) + 1
                
                # 변경 내역에 추가
                if '변경내역' not in info:
                    info['변경내역'] = []
                
                info['변경내역'].insert(0, {
                    "확인시각": datetime.now().isoformat(),
                    "변경내용": f"공포일자 변경 ({info['마지막공포일자']} -> {current_pub_date})",
                    "신구대조표": diff_file
                })
                
                # 변경내역 최대 10개 유지
                if len(info['변경내역']) > 10:
                    info['변경내역'] = info['변경내역'][:10]

            else:
                print(f"   ✅ 변경 없음")

            info['마지막확인'] = datetime.now().isoformat()

        self._save_tracked_laws()

        # 변경 이력 저장
        if updates:
            self._save_update_history(updates)

        print("\n" + "="*80)
        print(f"✅ 확인 완료 - {len(updates)}개 법령 변경됨")
        print("="*80)

        return updates

    def _save_update_history(self, updates: List[Dict]):
        """변경 이력 저장 (MongoDB 우선, fallback to file)"""
        if self.db and self.db.is_connected():
            self.db.save_update_history(updates)
        
        # Also save to local file as backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / "history" / f"updates_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "확인일시": datetime.now().isoformat(),
                "변경개수": len(updates),
                "변경목록": updates
            }, f, ensure_ascii=False, indent=2)

        print(f"💾 변경 이력 저장: {filename.name}")

    def list_tracked_laws(self):
        """추적 중인 법령 목록 출력"""
        if not self.tracked_laws:
            print("\n📋 추적 중인 법령이 없습니다.")
            return

        print("\n" + "="*80)
        print("📋 추적 중인 법령 목록")
        print("="*80)

        for i, (law_name, info) in enumerate(self.tracked_laws.items(), 1):
            print(f"\n{i}. {law_name}")
            print(f"   법령일련번호: {info['법령일련번호']}")
            print(f"   법령ID: {info['법령ID']}")
            print(f"   공포일자: {info['공포일자']}")
            print(f"   시행일자: {info['시행일자']}")
            print(f"   추가일시: {info['추가일시']}")
            print(f"   마지막 확인: {info['마지막확인'] or '없음'}")
            print(f"   변경 횟수: {info.get('변경횟수', 0)}회")

        print("="*80)

    def get_law_info(self, law_name: str):
        """특정 법령의 상세 정보 조회"""
        if law_name not in self.tracked_laws:
            print(f"❌ 추적 중이지 않은 법령: {law_name}")
            return None

        info = self.tracked_laws[law_name]
        law_mst_seq = info['법령일련번호']

        print(f"\n📋 {law_name} 상세 정보 조회")
        detail = self.get_law_detail(law_mst_seq)

        if detail and '기본정보' in detail:
            basic_info = detail['기본정보']
            print(f"\n법령명: {basic_info.get('법령명_한글')}")
            print(f"공포일자: {basic_info.get('공포일자')}")
            print(f"공포번호: {basic_info.get('공포번호')}")
            print(f"시행일자: {basic_info.get('시행일자')}")
            print(f"제개정구분: {basic_info.get('제개정구분')}")
            print(f"소관부처: {basic_info.get('소관부처')}")
            print(f"전화번호: {basic_info.get('전화번호')}")

        return detail


def main():
    """메인 함수"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print("="*80)
    print("🏛️  법령 추적 시스템")
    print("="*80)
    print(f"API 키: {api_key}")

    tracker = LawTracker(api_key)

    # 사용 예시
    print("\n" + "="*80)
    print("1️⃣  추적 대상 법령 추가")
    print("="*80)

    tracker.add_law("사립학교법")
    tracker.add_law("고등교육법")

    # 추적 목록 확인
    print("\n" + "="*80)
    print("2️⃣  추적 목록 확인")
    print("="*80)
    tracker.list_tracked_laws()

    # 업데이트 확인
    print("\n" + "="*80)
    print("3️⃣  변경사항 확인")
    print("="*80)
    updates = tracker.check_updates()

    if updates:
        print(f"\n🔔 {len(updates)}개의 법령이 변경되었습니다!")
        for update in updates:
            print(f"\n📋 {update['법령명']}")
            print(f"   이전: {update['이전공포일자']} (번호: {update['이전법령일련번호']})")
            print(f"   현재: {update['현재공포일자']} (번호: {update['현재법령일련번호']})")
    else:
        print("\n✅ 모든 법령이 최신 상태입니다.")


if __name__ == "__main__":
    main()
