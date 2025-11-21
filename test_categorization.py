#!/usr/bin/env python3
"""
법령 자동 분류 테스트
"""

from law_hierarchy import LawHierarchy

def test_auto_categorization():
    """자동 분류 테스트"""
    hierarchy = LawHierarchy()

    # law_list.txt에서 가져온 샘플 법령들
    test_laws = [
        "고등교육법",
        "고용정책기본법",
        "공공기관의 운영에 관한 법률",
        "공무원행동강령",
        "교원노조법",
        "교육공무원법",
        "교육공무원징계령",
        "교육기본법",
        "국가공무원법",
        "근로기준법",
        "근로기준법시행령",
        "사립학교법",
        "사립학교교직원연금법",
        "아동ㆍ청소년의성보호에관한법률",
        "학술진흥법",
        "정부조직법",
        "명예교수규칙",
        "대학설립ㆍ운영 규정",
    ]

    print("="*80)
    print("법령 자동 분류 테스트")
    print("="*80)

    # 카테고리별 통계
    category_count = {}

    for law_name in test_laws:
        info = hierarchy.get_law_info(law_name)
        category = info['category']
        description = info['description']

        # 카테고리 카운트
        category_count[category] = category_count.get(category, 0) + 1

        print(f"\n📋 {law_name}")
        print(f"   카테고리: {category}")
        print(f"   설명: {description}")

    print("\n" + "="*80)
    print("카테고리별 통계")
    print("="*80)

    for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{category:15s}: {count}개")

    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    test_auto_categorization()
