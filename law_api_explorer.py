#!/usr/bin/env python3
"""
국가법령정보센터 Open API 탐색 프로그램
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import json
from xml.etree import ElementTree as ET

# 환경 변수 로드
load_dotenv()

class LawAPIExplorer:
    """국가법령정보센터 API 탐색 클래스"""

    def __init__(self, api_key: str):
        self.api_key = api_key

        # 여러 API URL 시도
        self.base_urls = [
            "http://www.law.go.kr/DRF",
            "https://www.law.go.kr/DRF",
            "http://apis.data.go.kr/1170000/law",
        ]

        self.current_base_url = self.base_urls[0]

        # 알려진 주요 API 엔드포인트들
        self.endpoints = {
            "법령목록": "/lawSearch.do",
            "법령상세": "/lawService.do",
            "법령조문": "/lawService.do",
            "개정이유": "/RevsInfo.do",
            "법령연혁": "/HRCInfo.do",
            "판례목록": "/PrecSearch.do",
            "판례상세": "/PrecService.do",
            "행정규칙목록": "/AdmRulSearch.do",
            "행정규칙상세": "/AdmRulService.do",
            "자치법규목록": "/OrdinSearch.do",
            "자치법규상세": "/OrdinService.do",
        }

    def _make_request(self, endpoint: str, params: Dict) -> Optional[str]:
        """API 요청 수행 (여러 방식 시도)"""

        # API 키 파라미터 이름 후보들
        key_param_names = ['OC', 'serviceKey', 'key']

        # 모든 조합 시도
        for base_url in self.base_urls:
            for key_param in key_param_names:
                url = f"{base_url}{endpoint}"
                test_params = params.copy()
                test_params[key_param] = self.api_key

                try:
                    print(f"   시도: {url} (키 파라미터: {key_param})")
                    response = requests.get(url, params=test_params, timeout=10)

                    if response.status_code == 200:
                        print(f"   ✅ 성공!")
                        self.current_base_url = base_url  # 성공한 URL 저장
                        return response.text
                    else:
                        print(f"   ⚠️  상태 코드: {response.status_code}")
                        # 에러 응답 내용 확인
                        if response.text:
                            print(f"   📄 응답 내용: {response.text[:200]}")

                except requests.exceptions.RequestException as e:
                    print(f"   ⚠️  실패: {str(e)[:100]}")
                    continue

        print(f"❌ 모든 API 요청 방식 실패")
        return None

    def _parse_xml_response(self, xml_string: str) -> Dict:
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_string)
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            print(f"❌ XML 파싱 실패: {e}")
            return {"raw": xml_string}

    def _xml_to_dict(self, element) -> Dict:
        """XML 요소를 딕셔너리로 변환"""
        result = {}

        # 속성 추가
        if element.attrib:
            result['@attributes'] = element.attrib

        # 텍스트 내용
        if element.text and element.text.strip():
            if len(element) == 0:  # 자식 요소가 없으면
                return element.text.strip()
            result['#text'] = element.text.strip()

        # 자식 요소 처리
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # 이미 존재하면 리스트로 변환
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result if result else element.text

    def search_law(self, query: str, display: int = 5) -> Dict:
        """법령 검색

        Args:
            query: 검색어 (법령명)
            display: 표시할 결과 수
        """
        print(f"\n🔍 법령 검색: '{query}'")
        params = {
            'target': 'law',
            'query': query,
            'display': display,
            'type': 'XML'
        }

        response = self._make_request(self.endpoints["법령목록"], params)
        if response:
            return self._parse_xml_response(response)
        return {}

    def get_law_detail(self, law_mst_seq: str) -> Dict:
        """법령 상세 정보 조회

        Args:
            law_mst_seq: 법령 일련번호
        """
        print(f"\n📋 법령 상세 조회: {law_mst_seq}")
        params = {
            'target': 'law',
            'MST': law_mst_seq,
            'type': 'XML'
        }

        response = self._make_request(self.endpoints["법령상세"], params)
        if response:
            return self._parse_xml_response(response)
        return {}

    def get_law_revision_info(self, law_mst_seq: str) -> Dict:
        """법령 개정이유 조회

        Args:
            law_mst_seq: 법령 일련번호
        """
        print(f"\n🔄 개정이유 조회: {law_mst_seq}")
        params = {
            'MST': law_mst_seq,
            'type': 'XML'
        }

        response = self._make_request(self.endpoints["개정이유"], params)
        if response:
            return self._parse_xml_response(response)
        return {}

    def get_law_history(self, law_mst_seq: str) -> Dict:
        """법령 연혁 조회

        Args:
            law_mst_seq: 법령 일련번호
        """
        print(f"\n📜 법령 연혁 조회: {law_mst_seq}")
        params = {
            'MST': law_mst_seq,
            'type': 'XML'
        }

        response = self._make_request(self.endpoints["법령연혁"], params)
        if response:
            return self._parse_xml_response(response)
        return {}

    def test_all_endpoints(self, test_law_name: str = "사립학교법"):
        """모든 주요 엔드포인트 테스트"""
        print("="*60)
        print("🚀 국가법령정보센터 Open API 탐색 시작")
        print("="*60)

        # 1. 법령 검색
        search_result = self.search_law(test_law_name, display=3)

        if not search_result:
            print("\n⚠️  법령 검색에 실패했습니다.")
            return

        # 결과 출력
        print("\n✅ 검색 결과:")
        print(json.dumps(search_result, indent=2, ensure_ascii=False))

        # 법령 일련번호 추출 시도
        law_mst_seq = self._extract_law_mst_seq(search_result)

        if law_mst_seq:
            print(f"\n✅ 발견된 법령 일련번호: {law_mst_seq}")

            # 2. 법령 상세 조회
            detail = self.get_law_detail(law_mst_seq)
            if detail:
                print("\n✅ 상세 정보 조회 성공")
                print(json.dumps(detail, indent=2, ensure_ascii=False)[:500] + "...")

            # 3. 개정이유 조회
            revision = self.get_law_revision_info(law_mst_seq)
            if revision:
                print("\n✅ 개정이유 조회 성공")
                print(json.dumps(revision, indent=2, ensure_ascii=False)[:500] + "...")

            # 4. 법령 연혁 조회
            history = self.get_law_history(law_mst_seq)
            if history:
                print("\n✅ 법령 연혁 조회 성공")
                print(json.dumps(history, indent=2, ensure_ascii=False)[:500] + "...")

        print("\n" + "="*60)
        print("🎉 API 탐색 완료!")
        print("="*60)

    def _extract_law_mst_seq(self, search_result: Dict) -> Optional[str]:
        """검색 결과에서 법령 일련번호 추출"""
        try:
            # 구조가 다를 수 있으므로 여러 경로 시도
            if 'law' in search_result:
                laws = search_result['law']
                if isinstance(laws, list) and len(laws) > 0:
                    law = laws[0]
                elif isinstance(laws, dict):
                    law = laws
                else:
                    return None

                # 법령 일련번호 필드명은 다를 수 있음
                for key in ['법령일련번호', 'MST', '법령ID', 'mst', 'lawMstSeq']:
                    if key in law:
                        return str(law[key])

            # 다른 구조 시도
            if 'LawSearch' in search_result:
                law_search = search_result['LawSearch']
                if 'law' in law_search:
                    laws = law_search['law']
                    if isinstance(laws, list) and len(laws) > 0:
                        law = laws[0]
                        for key in ['법령일련번호', 'MST', '법령ID', 'mst', 'lawMstSeq']:
                            if key in law:
                                return str(law[key])

        except Exception as e:
            print(f"⚠️  법령 일련번호 추출 중 오류: {e}")

        return None


def main():
    """메인 함수"""
    api_key = os.getenv('LAW_API_KEY')

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    print(f"✅ API 키 로드 완료: {api_key}")

    explorer = LawAPIExplorer(api_key)

    # 테스트할 법령들
    test_laws = [
        "사립학교법",
        "고등교육법",
    ]

    for law_name in test_laws:
        explorer.test_all_endpoints(law_name)
        print("\n")


if __name__ == "__main__":
    main()
