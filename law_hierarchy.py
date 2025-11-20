#!/usr/bin/env python3
"""
법령 체계도 및 관계 매핑 시스템
"""

import json
from typing import Dict, List, Set
from pathlib import Path


class LawHierarchy:
    """법령 체계 및 관계 관리 클래스"""

    def __init__(self):
        # 법령 카테고리 정의
        self.categories = {
            "헌법": {"level": 0, "color": "#8B0000", "description": "대한민국 헌법"},
            "교육기본법": {"level": 1, "color": "#1E90FF", "description": "교육의 기본 원리"},
            "학교교육": {"level": 2, "color": "#32CD32", "description": "학교급별 교육"},
            "교원": {"level": 2, "color": "#FF8C00", "description": "교원 관련"},
            "학교운영": {"level": 2, "color": "#9370DB", "description": "학교 설립·운영"},
            "학생보호": {"level": 2, "color": "#DC143C", "description": "학생 안전·보호"},
            "교육행정": {"level": 2, "color": "#4682B4", "description": "교육 행정·재정"},
            "특별교육": {"level": 2, "color": "#20B2AA", "description": "특수·영재 교육"},
            "교육시설": {"level": 2, "color": "#DAA520", "description": "학원·도서관 등"},
            "산학협력": {"level": 2, "color": "#8B4513", "description": "산학협력·평생학습"},
            "시행령/규칙": {"level": 3, "color": "#708090", "description": "하위 법령"}
        }

        # 법령 정의 및 관계 매핑
        self.laws = {
            # 헌법
            "대한민국헌법": {
                "category": "헌법",
                "description": "대한민국의 최고 법규범",
                "related": ["교육기본법"]
            },

            # 기본법
            "교육기본법": {
                "category": "교육기본법",
                "description": "교육의 기본 이념과 방향",
                "related": ["초중등교육법", "고등교육법", "유아교육법", "평생교육법",
                          "사립학교법", "특수교육법", "영재교육진흥법"]
            },

            # 학교교육 - 학교급별
            "유아교육법": {
                "category": "학교교육",
                "description": "유치원 교육",
                "related": ["교육기본법", "학교보건법", "유아교육법 시행령", "유아교육법 시행규칙"]
            },
            "초중등교육법": {
                "category": "학교교육",
                "description": "초·중·고등학교 교육",
                "related": ["교육기본법", "교원지위법", "학교폭력예방법", "학교보건법",
                          "특수교육법", "초중등교육법 시행령", "초중등교육법 시행규칙"]
            },
            "고등교육법": {
                "category": "학교교육",
                "description": "대학교육",
                "related": ["교육기본법", "사립학교법", "국립대학법인법", "산학협력법",
                          "고등교육법 시행령", "고등교육법 시행규칙"]
            },
            "평생교육법": {
                "category": "학교교육",
                "description": "평생교육 진흥",
                "related": ["교육기본법", "학점인정법", "평생교육법 시행령", "평생교육법 시행규칙"]
            },

            # 학교운영
            "사립학교법": {
                "category": "학교운영",
                "description": "사립학교 설립·운영",
                "related": ["교육기본법", "고등교육법", "초중등교육법",
                          "사립학교교직원 연금법", "사립학교법 시행령"]
            },
            "국립대학법인법": {
                "category": "학교운영",
                "description": "국립대학의 법인화",
                "related": ["고등교육법", "국립대학법인법 시행령"]
            },

            # 교원
            "교원지위법": {
                "category": "교원",
                "description": "교원의 지위 향상 및 교육활동 보호",
                "related": ["초중등교육법", "교육공무원법", "교원노조법", "교원지위법 시행령"]
            },
            "교육공무원법": {
                "category": "교원",
                "description": "교육공무원의 자격·임용·보수",
                "related": ["교원지위법", "교육공무원법 시행령", "교육공무원임용령"]
            },
            "교원노조법": {
                "category": "교원",
                "description": "교원의 노동조합 설립 및 운영",
                "related": ["교원지위법", "교육공무원법", "교원노조법 시행령"]
            },
            "사립학교교직원 연금법": {
                "category": "교원",
                "description": "사립학교 교직원의 연금",
                "related": ["사립학교법", "사립학교교직원 연금법 시행령"]
            },

            # 학생보호
            "학교폭력예방법": {
                "category": "학생보호",
                "description": "학교폭력 예방 및 대책",
                "related": ["초중등교육법", "학교폭력예방법 시행령"]
            },
            "학교보건법": {
                "category": "학생보호",
                "description": "학생 및 교직원의 건강 보호·증진",
                "related": ["초중등교육법", "유아교육법", "학교보건법 시행령", "학교보건법 시행규칙"]
            },

            # 교육행정
            "지방교육자치법": {
                "category": "교육행정",
                "description": "지방교육의 자주성과 전문성 보장",
                "related": ["교육기본법", "지방교육재정교부금법", "지방교육자치법 시행령"]
            },
            "지방교육재정교부금법": {
                "category": "교육행정",
                "description": "지방교육재정의 확보",
                "related": ["지방교육자치법", "지방교육재정교부금법 시행령"]
            },

            # 특별교육
            "특수교육법": {
                "category": "특별교육",
                "description": "장애인 등에 대한 특수교육",
                "related": ["교육기본법", "초중등교육법", "특수교육법 시행령", "특수교육법 시행규칙"]
            },
            "영재교육진흥법": {
                "category": "특별교육",
                "description": "영재교육 진흥",
                "related": ["교육기본법", "초중등교육법", "영재교육진흥법 시행령"]
            },

            # 교육시설
            "학원법": {
                "category": "교육시설",
                "description": "학원의 설립·운영 및 과외교습",
                "related": ["평생교육법", "학원법 시행령", "학원법 시행규칙"]
            },
            "도서관법": {
                "category": "교육시설",
                "description": "도서관의 설립 및 운영",
                "related": ["평생교육법", "도서관법 시행령"]
            },
            "박물관 및 미술관 진흥법": {
                "category": "교육시설",
                "description": "박물관 및 미술관 진흥",
                "related": ["평생교육법", "박물관 및 미술관 진흥법 시행령"]
            },

            # 산학협력
            "산학협력법": {
                "category": "산학협력",
                "description": "산업교육진흥 및 산학연협력 촉진",
                "related": ["고등교육법", "평생교육법", "산학협력법 시행령"]
            },
            "학점인정법": {
                "category": "산학협력",
                "description": "학점인정 등에 관한 법률",
                "related": ["평생교육법", "고등교육법", "학점인정법 시행령"]
            },

            # ===== 시행령/규칙 =====

            # 학교교육 관련 시행령
            "유아교육법 시행령": {
                "category": "시행령/규칙",
                "description": "유아교육법 시행령",
                "related": ["유아교육법"]
            },
            "유아교육법 시행규칙": {
                "category": "시행령/규칙",
                "description": "유아교육법 시행규칙",
                "related": ["유아교육법"]
            },
            "초중등교육법 시행령": {
                "category": "시행령/규칙",
                "description": "초중등교육법 시행령",
                "related": ["초중등교육법"]
            },
            "초중등교육법 시행규칙": {
                "category": "시행령/규칙",
                "description": "초중등교육법 시행규칙",
                "related": ["초중등교육법"]
            },
            "고등교육법 시행령": {
                "category": "시행령/규칙",
                "description": "고등교육법 시행령",
                "related": ["고등교육법"]
            },
            "고등교육법 시행규칙": {
                "category": "시행령/규칙",
                "description": "고등교육법 시행규칙",
                "related": ["고등교육법"]
            },
            "평생교육법 시행령": {
                "category": "시행령/규칙",
                "description": "평생교육법 시행령",
                "related": ["평생교육법"]
            },
            "평생교육법 시행규칙": {
                "category": "시행령/규칙",
                "description": "평생교육법 시행규칙",
                "related": ["평생교육법"]
            },

            # 학교운영 관련 시행령
            "사립학교법 시행령": {
                "category": "시행령/규칙",
                "description": "사립학교법 시행령",
                "related": ["사립학교법"]
            },
            "국립대학법인법 시행령": {
                "category": "시행령/규칙",
                "description": "국립대학법인법 시행령",
                "related": ["국립대학법인법"]
            },

            # 교원 관련 시행령
            "교원지위법 시행령": {
                "category": "시행령/규칙",
                "description": "교원지위법 시행령",
                "related": ["교원지위법"]
            },
            "교육공무원법 시행령": {
                "category": "시행령/규칙",
                "description": "교육공무원법 시행령",
                "related": ["교육공무원법"]
            },
            "교육공무원임용령": {
                "category": "시행령/규칙",
                "description": "교육공무원의 임용에 관한 대통령령",
                "related": ["교육공무원법"]
            },
            "교원노조법 시행령": {
                "category": "시행령/규칙",
                "description": "교원노조법 시행령",
                "related": ["교원노조법"]
            },
            "사립학교교직원 연금법 시행령": {
                "category": "시행령/규칙",
                "description": "사립학교교직원 연금법 시행령",
                "related": ["사립학교교직원 연금법"]
            },

            # 학생보호 관련 시행령
            "학교폭력예방법 시행령": {
                "category": "시행령/규칙",
                "description": "학교폭력예방법 시행령",
                "related": ["학교폭력예방법"]
            },
            "학교보건법 시행령": {
                "category": "시행령/규칙",
                "description": "학교보건법 시행령",
                "related": ["학교보건법"]
            },
            "학교보건법 시행규칙": {
                "category": "시행령/규칙",
                "description": "학교보건법 시행규칙",
                "related": ["학교보건법"]
            },

            # 교육행정 관련 시행령
            "지방교육자치법 시행령": {
                "category": "시행령/규칙",
                "description": "지방교육자치법 시행령",
                "related": ["지방교육자치법"]
            },
            "지방교육재정교부금법 시행령": {
                "category": "시행령/규칙",
                "description": "지방교육재정교부금법 시행령",
                "related": ["지방교육재정교부금법"]
            },

            # 특별교육 관련 시행령
            "특수교육법 시행령": {
                "category": "시행령/규칙",
                "description": "특수교육법 시행령",
                "related": ["특수교육법"]
            },
            "특수교육법 시행규칙": {
                "category": "시행령/규칙",
                "description": "특수교육법 시행규칙",
                "related": ["특수교육법"]
            },
            "영재교육진흥법 시행령": {
                "category": "시행령/규칙",
                "description": "영재교육진흥법 시행령",
                "related": ["영재교육진흥법"]
            },

            # 교육시설 관련 시행령
            "학원법 시행령": {
                "category": "시행령/규칙",
                "description": "학원법 시행령",
                "related": ["학원법"]
            },
            "학원법 시행규칙": {
                "category": "시행령/규칙",
                "description": "학원법 시행규칙",
                "related": ["학원법"]
            },
            "도서관법 시행령": {
                "category": "시행령/규칙",
                "description": "도서관법 시행령",
                "related": ["도서관법"]
            },
            "박물관 및 미술관 진흥법 시행령": {
                "category": "시행령/규칙",
                "description": "박물관 및 미술관 진흥법 시행령",
                "related": ["박물관 및 미술관 진흥법"]
            },

            # 산학협력 관련 시행령
            "산학협력법 시행령": {
                "category": "시행령/규칙",
                "description": "산학협력법 시행령",
                "related": ["산학협력법"]
            },
            "학점인정법 시행령": {
                "category": "시행령/규칙",
                "description": "학점인정법 시행령",
                "related": ["학점인정법"]
            }
        }

    def get_law_info(self, law_name: str) -> Dict:
        """특정 법령의 정보 반환"""
        # 완전 일치 먼저 시도
        if law_name in self.laws:
            info = self.laws[law_name].copy()
            category = info["category"]
            info["category_info"] = self.categories[category]
            return info

        # 부분 일치 시도
        for full_name, law_info in self.laws.items():
            if law_name in full_name:
                info = law_info.copy()
                category = info["category"]
                info["category_info"] = self.categories[category]
                info["full_name"] = full_name
                return info

        # 찾지 못한 경우 기타 카테고리로 반환
        return {
            "category": "기타",
            "description": "미분류 법령",
            "related": [],
            "category_info": {"level": 2, "color": "#A9A9A9", "description": "기타 법령"},
            "full_name": law_name
        }

    def get_related_laws(self, law_name: str) -> List[str]:
        """특정 법령과 관련된 법령 목록 반환"""
        law_info = self.get_law_info(law_name)
        return law_info.get("related", [])

    def generate_graph_data(self, tracked_laws: List[str],
                           updated_laws: List[str] = None) -> Dict:
        """
        D3.js용 그래프 데이터 생성

        Args:
            tracked_laws: 추적 중인 법령 목록
            updated_laws: 업데이트된 법령 목록 (선택)
        """
        if updated_laws is None:
            updated_laws = []

        nodes = []
        links = []
        node_ids = set()

        # 추적 중인 법령과 관련 법령을 모두 노드로 추가
        laws_to_process = set(tracked_laws)

        # 관련 법령도 포함
        for law in tracked_laws:
            related = self.get_related_laws(law)
            laws_to_process.update(related)

        # 노드 생성
        for law_name in laws_to_process:
            law_info = self.get_law_info(law_name)
            full_name = law_info.get("full_name", law_name)

            # 상태 결정
            status = "normal"
            if law_name in tracked_laws or full_name in tracked_laws:
                if law_name in updated_laws or full_name in updated_laws:
                    status = "updated"  # 업데이트됨
                else:
                    status = "tracked"  # 추적 중

            node = {
                "id": full_name,
                "name": full_name,
                "category": law_info["category"],
                "description": law_info["description"],
                "color": law_info["category_info"]["color"],
                "level": law_info["category_info"]["level"],
                "status": status
            }

            nodes.append(node)
            node_ids.add(full_name)

        # 링크 생성
        for law_name in laws_to_process:
            law_info = self.get_law_info(law_name)
            source = law_info.get("full_name", law_name)

            for related_law in law_info.get("related", []):
                # 양방향 링크 중복 방지
                if related_law in node_ids:
                    # source < target 순서로 정렬하여 중복 방지
                    if source < related_law:
                        links.append({
                            "source": source,
                            "target": related_law
                        })

        # 카테고리 정보도 포함
        categories_used = {}
        for node in nodes:
            cat_name = node["category"]
            if cat_name not in categories_used:
                categories_used[cat_name] = self.categories.get(
                    cat_name,
                    {"level": 2, "color": "#A9A9A9", "description": "기타"}
                )

        return {
            "nodes": nodes,
            "links": links,
            "categories": categories_used
        }

    def get_all_categories(self) -> Dict:
        """모든 카테고리 정보 반환"""
        return self.categories

    def search_laws_by_category(self, category: str) -> List[str]:
        """특정 카테고리의 법령 목록 반환"""
        return [
            law_name
            for law_name, law_info in self.laws.items()
            if law_info["category"] == category
        ]


def main():
    """테스트용 메인 함수"""
    hierarchy = LawHierarchy()

    # 테스트: 추적 중인 법령
    tracked = ["사립학교법", "고등교육법", "교육기본법", "특수교육법"]
    updated = ["고등교육법"]

    # 그래프 데이터 생성
    graph_data = hierarchy.generate_graph_data(tracked, updated)

    print("노드 수:", len(graph_data["nodes"]))
    print("링크 수:", len(graph_data["links"]))
    print("카테고리:", list(graph_data["categories"].keys()))

    # JSON 출력 (테스트)
    print("\n그래프 데이터:")
    print(json.dumps(graph_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
