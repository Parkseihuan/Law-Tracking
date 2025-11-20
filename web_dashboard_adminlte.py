#!/usr/bin/env python3
"""
법령 추적 시스템 - AdminLTE 웹 대시보드
"""

import os
import json
from flask import Flask, render_template, jsonify, request
from pathlib import Path
from datetime import datetime
from law_tracker import LawTracker
from law_hierarchy import LawHierarchy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글 지원

# 전역 변수
api_key = os.getenv('LAW_API_KEY')
tracker = LawTracker(api_key) if api_key else None
hierarchy = LawHierarchy()


# ==================== 페이지 라우트 ====================

@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('adminlte/dashboard.html')


@app.route('/laws')
def laws_page():
    """법령 목록 페이지"""
    laws = tracker.tracked_laws if tracker else {}
    return render_template('adminlte/laws.html', laws=laws)


@app.route('/hierarchy')
def law_hierarchy_page():
    """법령 체계도 페이지"""
    return render_template('law_hierarchy.html')


@app.route('/updates')
def updates_page():
    """변경 이력 페이지"""
    return render_template('adminlte/updates.html')


@app.route('/statistics')
def statistics_page():
    """통계 페이지"""
    return render_template('adminlte/statistics.html')


# ==================== API 엔드포인트 ====================

@app.route('/api/laws')
def get_laws():
    """법령 목록 조회 (AdminLTE용)"""
    if not tracker:
        return jsonify([])

    laws = []
    for law_name, info in tracker.tracked_laws.items():
        laws.append({
            "법령명": law_name,
            "법령일련번호": info.get('법령일련번호', ''),
            "법령ID": info.get('법령ID', ''),
            "법령종류명": info.get('법령종류명', ''),
            "공포일자": info.get('공포일자', ''),
            "시행일자": info.get('시행일자', ''),
            "소관부처명": info.get('소관부처명', ''),
            "마지막확인": info.get('마지막확인', ''),
            "변경횟수": info.get('변경횟수', 0),
            "변경내역": info.get('변경내역', [])
        })

    return jsonify(laws)


@app.route('/api/law-detail')
def get_law_detail():
    """법령 상세 정보"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    law_name = request.args.get('name')
    if not law_name or law_name not in tracker.tracked_laws:
        return jsonify({"error": "법령을 찾을 수 없습니다"}), 404

    info = tracker.tracked_laws[law_name]
    return jsonify({
        "법령명": law_name,
        "법령일련번호": info.get('법령일련번호', ''),
        "법령ID": info.get('법령ID', ''),
        "법령종류명": info.get('법령종류명', ''),
        "공포일자": info.get('공포일자', ''),
        "시행일자": info.get('시행일자', ''),
        "소관부처명": info.get('소관부처명', ''),
        "마지막확인": info.get('마지막확인', ''),
        "변경횟수": info.get('변경횟수', 0),
        "변경내역": info.get('변경내역', [])
    })


@app.route('/api/law-updates')
def get_law_updates():
    """업데이트된 법령 목록"""
    if not tracker:
        return jsonify([])

    updates = []
    for law_name, info in tracker.tracked_laws.items():
        if info.get('변경횟수', 0) > 0:
            updates.append({
                "법령명": law_name,
                "변경횟수": info['변경횟수'],
                "마지막확인": info.get('마지막확인', '')
            })

    # 변경횟수 순으로 정렬
    updates.sort(key=lambda x: x['변경횟수'], reverse=True)
    return jsonify(updates)


@app.route('/api/statistics')
def get_statistics():
    """통계 정보"""
    if not tracker:
        return jsonify({
            "total_laws": 0,
            "updated_laws": 0,
            "categories": 0,
            "last_check": None
        })

    total_laws = len(tracker.tracked_laws)
    updated_laws = sum(1 for info in tracker.tracked_laws.values() if info.get('변경횟수', 0) > 0)

    # 카테고리 수
    tracked_law_names = list(tracker.tracked_laws.keys())
    if tracked_law_names:
        graph_data = hierarchy.generate_graph_data(tracked_law_names)
        categories = len(graph_data.get('categories', {}))
    else:
        categories = 0

    # 마지막 확인 시간
    last_checks = [info.get('마지막확인') for info in tracker.tracked_laws.values() if info.get('마지막확인')]
    last_check = max(last_checks) if last_checks else None

    return jsonify({
        "total_laws": total_laws,
        "updated_laws": updated_laws,
        "categories": categories,
        "last_check": last_check
    })


@app.route('/api/check-updates', methods=['POST'])
def check_updates():
    """변경사항 확인"""
    if not tracker:
        return jsonify({"success": False, "error": "API 키가 설정되지 않았습니다"}), 500

    try:
        updates = tracker.check_updates()
        return jsonify({
            "success": True,
            "updated": len(updates),
            "changes": updates
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/add-law', methods=['POST'])
def add_law():
    """법령 추가"""
    if not tracker:
        return jsonify({"success": False, "message": "API 키가 설정되지 않았습니다"}), 500

    data = request.get_json()
    law_name = data.get('law_name')

    if not law_name:
        return jsonify({"success": False, "message": "법령명이 필요합니다"}), 400

    try:
        success = tracker.add_law(law_name)
        if success:
            return jsonify({"success": True, "message": f"{law_name} 추가 완료"})
        else:
            return jsonify({"success": False, "message": "법령을 찾을 수 없습니다"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/remove-law', methods=['POST'])
def remove_law():
    """법령 제거"""
    if not tracker:
        return jsonify({"success": False, "message": "API 키가 설정되지 않았습니다"}), 500

    data = request.get_json()
    law_name = data.get('law_name')

    if not law_name:
        return jsonify({"success": False, "message": "법령명이 필요합니다"}), 400

    try:
        success = tracker.remove_law(law_name)
        return jsonify({"success": success, "message": f"{law_name} 제거 완료"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/law-hierarchy')
def get_law_hierarchy():
    """법령 체계도 데이터 조회"""
    if not tracker:
        return jsonify({"nodes": [], "links": [], "categories": {}})

    try:
        # 추적 중인 법령 목록
        tracked_laws = list(tracker.tracked_laws.keys())

        # 업데이트된 법령 목록
        updated_laws = [
            law_name
            for law_name, info in tracker.tracked_laws.items()
            if info.get('변경횟수', 0) > 0
        ]

        # 그래프 데이터 생성
        graph_data = hierarchy.generate_graph_data(tracked_laws, updated_laws)
        return jsonify(graph_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    else:
        print("="*80)
        print("🌐 법령 추적 웹 대시보드 (AdminLTE)")
        print("="*80)
        print(f"\n🚀 서버 시작: http://localhost:5000")
        print("📌 브라우저에서 위 주소로 접속하세요\n")
        print("💡 AdminLTE 템플릿 적용")
        print("   - 대시보드: http://localhost:5000/")
        print("   - 법령 목록: http://localhost:5000/laws")
        print("   - 법령 체계도: http://localhost:5000/hierarchy")
        print("\n종료하려면 Ctrl+C를 누르세요")
        print("="*80 + "\n")

        app.run(debug=True, host='0.0.0.0', port=5000)
