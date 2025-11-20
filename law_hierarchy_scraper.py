#!/usr/bin/env python3
"""
법령 체계도 웹 크롤링
국가법령정보센터에서 실제 법령 체계도 데이터를 수집
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class LawHierarchyScraper:
    """법령 체계도 크롤러"""

    def __init__(self, data_dir: str = "data"):
        self.base_url = "https://www.law.go.kr"
        self.data_dir = Path(data_dir)
        self.hierarchy_file = self.data_dir / "law_relationships.json"

        # 디렉토리 생성
        self.data_dir.mkdir(exist_ok=True)

        # 브라우저 헤더 설정 (403 방지)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

        # 세션 사용 (쿠키 유지)
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 기존 관계 데이터 로드
        self.relationships = self._load_relationships()

    def _load_relationships(self) -> Dict:
        """저장된 관계 데이터 로드"""
        if self.hierarchy_file.exists():
            with open(self.hierarchy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_relationships(self):
        """관계 데이터 저장"""
        with open(self.hierarchy_file, 'w', encoding='utf-8') as f:
            json.dump(self.relationships, f, ensure_ascii=False, indent=2)
        print(f"💾 관계 데이터 저장: {self.hierarchy_file}")

    def scrape_hierarchy(self, law_mst_seq: str, law_name: str = None) -> Optional[Dict]:
        """
        법령 체계도 크롤링

        Args:
            law_mst_seq: 법령일련번호 (lsiSeq)
            law_name: 법령명 (선택)

        Returns:
            법령 관계 정보 딕셔너리
        """
        url = f"{self.base_url}/LSW//lsStmdInfoP.do"
        params = {
            'lsiSeq': law_mst_seq,
            'ancYnChk': '0'
        }

        print(f"\n🔍 법령 체계도 크롤링: {law_name or law_mst_seq}")
        print(f"   URL: {url}?lsiSeq={law_mst_seq}")

        try:
            # 요청 전 잠시 대기 (서버 부하 방지)
            time.sleep(1)

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return self._parse_hierarchy_page(response.text, law_name, law_mst_seq)
            else:
                print(f"   ❌ 요청 실패: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return None

    def _parse_hierarchy_page(self, html: str, law_name: str, law_mst_seq: str) -> Dict:
        """HTML 파싱하여 법령 관계 추출"""
        soup = BeautifulSoup(html, 'html.parser')

        result = {
            "법령명": law_name,
            "법령일련번호": law_mst_seq,
            "수집일시": datetime.now().isoformat(),
            "상위법령": [],
            "하위법령": [],
            "관련법령": []
        }

        # 체계도 영역 찾기
        # 일반적으로 <div class="law_tree">, <ul class="tree">, <div id="lawTree"> 등의 구조 사용

        # 패턴 1: law_tree 클래스
        tree_area = soup.find('div', class_='law_tree')
        if not tree_area:
            # 패턴 2: tree 클래스
            tree_area = soup.find('ul', class_='tree')
        if not tree_area:
            # 패턴 3: lawTree ID
            tree_area = soup.find('div', id='lawTree')
        if not tree_area:
            # 패턴 4: 테이블 구조
            tree_area = soup.find('table', class_='lawStmdTbl')

        if tree_area:
            # 링크 요소에서 법령명 추출
            links = tree_area.find_all('a')

            for link in links:
                related_law_name = link.get_text(strip=True)

                if not related_law_name or related_law_name == law_name:
                    continue

                # 링크에서 lsiSeq 추출
                href = link.get('href', '')
                related_seq = None
                if 'lsiSeq=' in href:
                    try:
                        related_seq = href.split('lsiSeq=')[1].split('&')[0]
                    except:
                        pass

                # 관계 유형 판단 (상위/하위/관련)
                # 부모 요소의 클래스나 텍스트로 판단
                parent_li = link.find_parent('li')
                parent_div = link.find_parent('div')

                relation_type = "관련법령"  # 기본값

                # 클래스명으로 유형 판단
                if parent_li:
                    class_names = parent_li.get('class', [])
                    if 'parent' in class_names or 'upper' in class_names:
                        relation_type = "상위법령"
                    elif 'child' in class_names or 'lower' in class_names:
                        relation_type = "하위법령"

                # 텍스트 패턴으로 유형 판단
                if "시행령" in related_law_name or "시행규칙" in related_law_name:
                    relation_type = "하위법령"
                elif related_law_name.endswith("법") and law_name and (
                    law_name.startswith(related_law_name.replace("법", "")) or
                    "시행령" in law_name or "시행규칙" in law_name
                ):
                    relation_type = "상위법령"

                # 관계 정보 저장
                relation_info = {
                    "법령명": related_law_name,
                    "법령일련번호": related_seq
                }

                if relation_type == "상위법령":
                    result["상위법령"].append(relation_info)
                elif relation_type == "하위법령":
                    result["하위법령"].append(relation_info)
                else:
                    result["관련법령"].append(relation_info)

            print(f"   ✅ 추출 완료:")
            print(f"      상위법령: {len(result['상위법령'])}개")
            print(f"      하위법령: {len(result['하위법령'])}개")
            print(f"      관련법령: {len(result['관련법령'])}개")
        else:
            print(f"   ⚠️  체계도 영역을 찾을 수 없습니다")

        return result

    def scrape_all_tracked_laws(self, tracked_laws: Dict):
        """
        추적 중인 모든 법령의 체계도 크롤링

        Args:
            tracked_laws: law_tracker.py의 tracked_laws 딕셔너리
        """
        print("\n" + "="*80)
        print("🕷️  법령 체계도 일괄 크롤링 시작")
        print("="*80)

        total = len(tracked_laws)
        success_count = 0

        for i, (law_name, info) in enumerate(tracked_laws.items(), 1):
            print(f"\n[{i}/{total}] {law_name}")

            law_mst_seq = info.get('법령일련번호')
            if not law_mst_seq:
                print("   ⚠️  법령일련번호 없음")
                continue

            # 이미 크롤링한 경우 스킵 (최근 7일 이내)
            if law_name in self.relationships:
                collected_date = self.relationships[law_name].get('수집일시')
                if collected_date:
                    try:
                        collected_dt = datetime.fromisoformat(collected_date)
                        days_ago = (datetime.now() - collected_dt).days
                        if days_ago < 7:
                            print(f"   ⏭️  최근 크롤링됨 ({days_ago}일 전)")
                            success_count += 1
                            continue
                    except:
                        pass

            # 크롤링 실행
            result = self.scrape_hierarchy(law_mst_seq, law_name)

            if result:
                self.relationships[law_name] = result
                success_count += 1

                # 중간 저장 (10개마다)
                if i % 10 == 0:
                    self._save_relationships()

        # 최종 저장
        self._save_relationships()

        print("\n" + "="*80)
        print(f"✅ 크롤링 완료: {success_count}/{total}개 성공")
        print("="*80)

    def get_all_relationships(self) -> Dict:
        """저장된 모든 관계 데이터 반환"""
        return self.relationships

    def get_law_relationships(self, law_name: str) -> Optional[Dict]:
        """특정 법령의 관계 데이터 반환"""
        return self.relationships.get(law_name)


def main():
    """테스트 함수"""
    scraper = LawHierarchyScraper()

    # 테스트: 사립학교법 체계도 크롤링 (예시 lsiSeq)
    # 실제 사용 시에는 law_tracker.py의 tracked_laws에서 lsiSeq를 가져옴

    test_law = {
        "법령명": "사립학교법",
        "법령일련번호": "000273"  # 예시 (실제는 law_tracker에서 조회)
    }

    result = scraper.scrape_hierarchy(
        test_law["법령일련번호"],
        test_law["법령명"]
    )

    if result:
        print("\n📋 크롤링 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
