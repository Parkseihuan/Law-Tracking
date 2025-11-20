#!/usr/bin/env python3
"""
법령 체계도 시스템 데모 (API 없이 작동)
"""

from law_hierarchy import LawHierarchy
import json


def demo():
    """법령 체계도 시스템 데모"""

    print("="*80)
    print("📊 법령 체계도 시스템 데모 (하드코딩된 관계 + 자동 추론)")
    print("="*80)

    hierarchy = LawHierarchy()

    # 샘플 법령 목록
    tracked_laws = [
        "교육기본법",
        "사립학교법",
        "사립학교법 시행령",
        "교육공무원법",
        "교육공무원법 시행령",
        "교육공무원임용령",
        "근로기준법",
        "근로기준법 시행령",
        "근로기준법 시행규칙"
    ]

    # 업데이트된 법령 (예시)
    updated_laws = ["사립학교법", "근로기준법"]

    print(f"\n✅ 추적 중인 법령: {len(tracked_laws)}개")
    for i, law in enumerate(tracked_laws, 1):
        status = "🔴 업데이트됨" if law in updated_laws else "📘 추적 중"
        print(f"   {i}. {law} {status}")

    # 그래프 데이터 생성
    print("\n🔄 법령 관계 그래프 생성 중...")
    graph_data = hierarchy.generate_graph_data(tracked_laws, updated_laws)

    print(f"\n📋 생성된 그래프 데이터:")
    print(f"   노드(법령) 수: {len(graph_data['nodes'])}개")
    print(f"   링크(관계) 수: {len(graph_data['links'])}개")
    print(f"   카테고리 수: {len(graph_data['categories'])}개")

    # 노드 상세 정보
    print("\n📌 법령 노드 정보:")
    for node in graph_data['nodes']:
        status_emoji = {
            "tracked": "📘",
            "updated": "🔴",
            "normal": "📄"
        }.get(node['status'], "📄")

        print(f"\n   {status_emoji} {node['name']}")
        print(f"      카테고리: {node['category']}")
        print(f"      설명: {node['description']}")
        print(f"      상태: {node['status']}")

    # 관계(링크) 정보
    print("\n🔗 법령 간 관계:")
    for link in graph_data['links']:
        print(f"   {link['source']} ↔ {link['target']}")

    # 관계 분석
    print("\n📊 관계 분석:")
    for law in tracked_laws:
        related = hierarchy.get_related_laws(law)
        if related:
            print(f"\n   {law}:")
            for r in related[:5]:  # 최대 5개만
                print(f"      → {r}")

    # JSON 저장
    output_file = "demo_graph_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 그래프 데이터 저장: {output_file}")

    print("\n" + "="*80)
    print("✅ 데모 완료!")
    print("="*80)
    print("\n💡 웹 대시보드에서 시각화를 확인하려면:")
    print("   python web_dashboard.py")
    print("   브라우저에서 http://localhost:5000/hierarchy 접속")


if __name__ == "__main__":
    demo()
