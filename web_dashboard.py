#!/usr/bin/env python3
"""
법령 추적 시스템 - 웹 대시보드
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


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/tracked-laws')
def get_tracked_laws():
    """추적 중인 법령 목록 조회"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    laws = []
    for law_name, info in tracker.tracked_laws.items():
        laws.append({
            "법령명": law_name,
            "법령일련번호": info['법령일련번호'],
            "법령ID": info['법령ID'],
            "공포일자": info['공포일자'],
            "시행일자": info['시행일자'],
            "마지막확인": info['마지막확인'],
            "변경횟수": info.get('변경횟수', 0)
        })

    return jsonify({
        "총개수": len(laws),
        "법령목록": laws
    })


@app.route('/api/check-updates', methods=['POST'])
def check_updates():
    """변경사항 확인"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    try:
        updates = tracker.check_updates()
        return jsonify({
            "성공": True,
            "변경개수": len(updates),
            "변경목록": updates
        })
    except Exception as e:
        return jsonify({"성공": False, "오류": str(e)}), 500


@app.route('/api/add-law', methods=['POST'])
def add_law():
    """법령 추가"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    data = request.get_json()
    law_name = data.get('법령명')

    if not law_name:
        return jsonify({"성공": False, "오류": "법령명이 필요합니다"}), 400

    try:
        success = tracker.add_law(law_name)
        return jsonify({"성공": success, "법령명": law_name})
    except Exception as e:
        return jsonify({"성공": False, "오류": str(e)}), 500


@app.route('/api/bulk-add-laws', methods=['POST'])
def bulk_add_laws():
    """여러 법령 일괄 추가"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    data = request.get_json()
    laws_text = data.get('법령목록', '')

    if not laws_text:
        return jsonify({"성공": False, "오류": "법령 목록이 필요합니다"}), 400

    # 텍스트 파싱 (줄바꿈, 쉼표, 세미콜론으로 구분)
    law_names = []
    for line in laws_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # 쉼표나 세미콜론으로 구분된 경우
        for name in line.replace(';', ',').split(','):
            name = name.strip()
            if name:
                law_names.append(name)

    if not law_names:
        return jsonify({"성공": False, "오류": "추가할 법령이 없습니다"}), 400

    results = {
        "성공": [],
        "실패": [],
        "건너뛰기": []
    }

    for law_name in law_names:
        try:
            # 이미 추적 중인지 확인
            if law_name in tracker.tracked_laws:
                results["건너뛰기"].append(law_name)
                continue

            success = tracker.add_law(law_name)
            if success:
                results["성공"].append(law_name)
            else:
                results["실패"].append(law_name)
        except Exception as e:
            results["실패"].append(f"{law_name} (오류: {str(e)})")

    return jsonify({
        "성공": True,
        "결과": results,
        "총개수": len(law_names),
        "성공개수": len(results["성공"]),
        "실패개수": len(results["실패"]),
        "건너뛰기개수": len(results["건너뛰기"])
    })


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """파일 업로드하여 법령 추가"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    if 'file' not in request.files:
        return jsonify({"성공": False, "오류": "파일이 없습니다"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"성공": False, "오류": "파일이 선택되지 않았습니다"}), 400

    # 파일 확장자 확인
    filename = file.filename.lower()
    if not (filename.endswith('.txt') or filename.endswith('.csv')):
        return jsonify({"성공": False, "오류": "txt 또는 csv 파일만 가능합니다"}), 400

    try:
        # 파일 내용 읽기
        content = file.read().decode('utf-8')

        # CSV 파일인 경우
        if filename.endswith('.csv'):
            law_names = []
            for line in content.split('\n'):
                # CSV의 첫 번째 컬럼만 사용
                parts = line.split(',')
                if parts:
                    name = parts[0].strip()
                    if name and not name.startswith('#'):
                        law_names.append(name)
        else:
            # TXT 파일
            law_names = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    law_names.append(line)

        if not law_names:
            return jsonify({"성공": False, "오류": "파일에 법령이 없습니다"}), 400

        results = {
            "성공": [],
            "실패": [],
            "건너뛰기": []
        }

        for law_name in law_names:
            try:
                # 이미 추적 중인지 확인
                if law_name in tracker.tracked_laws:
                    results["건너뛰기"].append(law_name)
                    continue

                success = tracker.add_law(law_name)
                if success:
                    results["성공"].append(law_name)
                else:
                    results["실패"].append(law_name)
            except Exception as e:
                results["실패"].append(f"{law_name} (오류: {str(e)})")

        return jsonify({
            "성공": True,
            "결과": results,
            "총개수": len(law_names),
            "성공개수": len(results["성공"]),
            "실패개수": len(results["실패"]),
            "건너뛰기개수": len(results["건너뛰기"])
        })

    except Exception as e:
        return jsonify({"성공": False, "오류": str(e)}), 500


@app.route('/api/remove-law', methods=['POST'])
def remove_law():
    """법령 제거"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    data = request.get_json()
    law_name = data.get('법령명')

    if not law_name:
        return jsonify({"성공": False, "오류": "법령명이 필요합니다"}), 400

    try:
        success = tracker.remove_law(law_name)
        return jsonify({"성공": success, "법령명": law_name})
    except Exception as e:
        return jsonify({"성공": False, "오류": str(e)}), 500


@app.route('/api/history')
def get_history():
    """변경 이력 조회"""
    history_dir = Path("data/history")

    if not history_dir.exists():
        return jsonify({"이력": []})

    history_files = sorted(history_dir.glob("*.json"), reverse=True)
    history_list = []

    for file in history_files[:10]:  # 최근 10개만
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            history_list.append(data)

    return jsonify({"이력": history_list})


@app.route('/api/stats')
def get_stats():
    """통계 정보"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    # 기본 통계
    stats = {
        "추적법령수": len(tracker.tracked_laws),
        "총변경횟수": sum(info.get('변경횟수', 0) for info in tracker.tracked_laws.values()),
        "마지막확인": None
    }

    # 마지막 확인 시간
    last_checks = [info.get('마지막확인') for info in tracker.tracked_laws.values() if info.get('마지막확인')]
    if last_checks:
        stats["마지막확인"] = max(last_checks)

    # 변경 이력 파일 개수
    history_dir = Path("data/history")
    if history_dir.exists():
        stats["이력파일수"] = len(list(history_dir.glob("*.json")))
    else:
        stats["이력파일수"] = 0

    return jsonify(stats)


@app.route('/hierarchy')
def law_hierarchy_page():
    """법령 체계도 페이지"""
    return render_template('law_hierarchy.html')


@app.route('/api/law-hierarchy')
def get_law_hierarchy():
    """법령 체계도 데이터 조회"""
    if not tracker:
        return jsonify({"error": "API 키가 설정되지 않았습니다"}), 500

    try:
        # 추적 중인 법령 목록
        tracked_laws = list(tracker.tracked_laws.keys())

        # 업데이트된 법령 목록 (변경횟수가 1 이상인 법령)
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


# HTML 템플릿 생성
def create_templates():
    """템플릿 폴더 및 파일 생성"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    index_html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>법령 추적 대시보드</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header-controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .header-controls .btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
        }

        .header-controls .btn:hover {
            background: white;
            color: #667eea;
            transform: translateY(-2px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-card h3 {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .section h2 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .btn-secondary {
            background: #6c757d;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        .btn-danger {
            background: #dc3545;
        }

        .btn-danger:hover {
            background: #c82333;
        }

        .law-list {
            list-style: none;
        }

        .law-item {
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }

        .law-item h4 {
            font-size: 18px;
            margin-bottom: 10px;
            color: #333;
        }

        .law-item .detail {
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .input-group input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }

        .tab-btn {
            background: none;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }

        .tab-btn:hover {
            color: #667eea;
        }

        .tab-btn.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            resize: vertical;
        }

        input[type="file"] {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            width: 100%;
            cursor: pointer;
        }

        .result-box {
            margin-top: 15px;
            padding: 15px;
            border-radius: 5px;
        }

        .result-success {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }

        .result-warning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
        }

        .result-error {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
        }

        .result-item {
            margin: 5px 0;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .loading.show {
            display: block;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ 법령 추적 대시보드</h1>
            <p>국가법령정보센터 Open API 기반 법령 개정 모니터링</p>
            <div class="header-controls">
                <a href="/hierarchy" class="btn">
                    <span>⚖️</span>
                    <span>법령 체계도 보기</span>
                </a>
            </div>
        </div>

        <!-- 통계 -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>추적 중인 법령</h3>
                <div class="value" id="stat-laws">0</div>
            </div>
            <div class="stat-card">
                <h3>총 변경 횟수</h3>
                <div class="value" id="stat-changes">0</div>
            </div>
            <div class="stat-card">
                <h3>이력 파일</h3>
                <div class="value" id="stat-history">0</div>
            </div>
        </div>

        <!-- 변경사항 확인 -->
        <div class="section">
            <h2>🔍 변경사항 확인</h2>
            <button class="btn" onclick="checkUpdates()">지금 확인하기</button>
            <div class="loading" id="loading-updates">
                <div class="spinner"></div>
                <p>변경사항을 확인하는 중...</p>
            </div>
            <div id="update-results"></div>
        </div>

        <!-- 법령 추가 -->
        <div class="section">
            <h2>➕ 법령 추가</h2>

            <!-- 탭 메뉴 -->
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('single')">단일 추가</button>
                <button class="tab-btn" onclick="switchTab('multiple')">여러 개 추가</button>
                <button class="tab-btn" onclick="switchTab('file')">파일 업로드</button>
            </div>

            <!-- 단일 추가 -->
            <div id="tab-single" class="tab-content active">
                <div class="input-group">
                    <input type="text" id="law-name-input" placeholder="법령명 입력 (예: 교육기본법)">
                    <button class="btn" onclick="addLaw()">추가</button>
                </div>
            </div>

            <!-- 여러 개 추가 -->
            <div id="tab-multiple" class="tab-content">
                <p style="color: #666; margin-bottom: 10px;">
                    여러 법령을 한 번에 입력하세요 (한 줄에 하나씩 또는 쉼표로 구분)
                </p>
                <textarea id="bulk-laws-input" placeholder="예시:
사립학교법
고등교육법, 교육기본법
초중등교육법"></textarea>
                <button class="btn" onclick="bulkAddLaws()" style="margin-top: 10px;">일괄 추가</button>
                <div id="bulk-result"></div>
            </div>

            <!-- 파일 업로드 -->
            <div id="tab-file" class="tab-content">
                <p style="color: #666; margin-bottom: 10px;">
                    txt 또는 csv 파일을 업로드하세요 (한 줄에 법령명 하나씩)
                </p>
                <input type="file" id="file-input" accept=".txt,.csv" style="margin-bottom: 10px;">
                <button class="btn" onclick="uploadFile()">파일 업로드</button>
                <div id="file-result"></div>
            </div>
        </div>

        <!-- 추적 중인 법령 목록 -->
        <div class="section">
            <h2>📋 추적 중인 법령</h2>
            <button class="btn btn-secondary" onclick="refreshLaws()">새로고침</button>
            <ul class="law-list" id="law-list">
                <li class="loading show">
                    <div class="spinner"></div>
                    <p>법령 목록을 불러오는 중...</p>
                </li>
            </ul>
        </div>
    </div>

    <script>
        // 페이지 로드 시 데이터 가져오기
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadLaws();
        });

        // 통계 로드
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                document.getElementById('stat-laws').textContent = data.추적법령수;
                document.getElementById('stat-changes').textContent = data.총변경횟수;
                document.getElementById('stat-history').textContent = data.이력파일수;
            } catch (error) {
                console.error('통계 로드 실패:', error);
            }
        }

        // 법령 목록 로드
        async function loadLaws() {
            try {
                const response = await fetch('/api/tracked-laws');
                const data = await response.json();

                const lawList = document.getElementById('law-list');
                lawList.innerHTML = '';

                if (data.법령목록.length === 0) {
                    lawList.innerHTML = '<li style="text-align: center; padding: 20px; color: #999;">추적 중인 법령이 없습니다</li>';
                    return;
                }

                data.법령목록.forEach(law => {
                    const li = document.createElement('li');
                    li.className = 'law-item';
                    li.innerHTML = `
                        <h4>${law.법령명}</h4>
                        <div class="detail">📋 법령일련번호: ${law.법령일련번호}</div>
                        <div class="detail">🆔 법령ID: ${law.법령ID}</div>
                        <div class="detail">📅 공포일자: ${law.공포일자}</div>
                        <div class="detail">🚀 시행일자: ${law.시행일자}</div>
                        <div class="detail">🔄 변경 횟수: ${law.변경횟수}회</div>
                        <div class="detail">🕐 마지막 확인: ${law.마지막확인 || '없음'}</div>
                        <button class="btn btn-danger" style="margin-top: 10px;" onclick="removeLaw('${law.법령명}')">제거</button>
                    `;
                    lawList.appendChild(li);
                });
            } catch (error) {
                console.error('법령 목록 로드 실패:', error);
                document.getElementById('law-list').innerHTML = '<li style="color: red;">법령 목록을 불러오는데 실패했습니다</li>';
            }
        }

        // 변경사항 확인
        async function checkUpdates() {
            const loading = document.getElementById('loading-updates');
            const results = document.getElementById('update-results');

            loading.classList.add('show');
            results.innerHTML = '';

            try {
                const response = await fetch('/api/check-updates', { method: 'POST' });
                const data = await response.json();

                loading.classList.remove('show');

                if (data.변경개수 > 0) {
                    results.innerHTML = `
                        <div style="margin-top: 20px; padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 5px;">
                            <h3 style="color: #155724;">🔔 ${data.변경개수}개 법령이 변경되었습니다!</h3>
                            ${data.변경목록.map(update => `
                                <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;">
                                    <strong>${update.법령명}</strong><br>
                                    이전: ${update.이전공포일자} (번호: ${update.이전법령일련번호})<br>
                                    현재: ${update.현재공포일자} (번호: ${update.현재법령일련번호})
                                </div>
                            `).join('')}
                        </div>
                    `;
                } else {
                    results.innerHTML = `
                        <div style="margin-top: 20px; padding: 15px; background: #d1ecf1; border-left: 4px solid #17a2b8; border-radius: 5px;">
                            <h3 style="color: #0c5460;">✅ 모든 법령이 최신 상태입니다</h3>
                        </div>
                    `;
                }

                loadStats();
                loadLaws();
            } catch (error) {
                loading.classList.remove('show');
                results.innerHTML = `
                    <div style="margin-top: 20px; padding: 15px; background: #f8d7da; border-left: 4px solid #dc3545; border-radius: 5px;">
                        <h3 style="color: #721c24;">❌ 오류 발생: ${error.message}</h3>
                    </div>
                `;
            }
        }

        // 법령 추가
        async function addLaw() {
            const input = document.getElementById('law-name-input');
            const lawName = input.value.trim();

            if (!lawName) {
                alert('법령명을 입력해주세요');
                return;
            }

            try {
                const response = await fetch('/api/add-law', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 법령명: lawName })
                });

                const data = await response.json();

                if (data.성공) {
                    alert(`${lawName}이(가) 추가되었습니다`);
                    input.value = '';
                    loadStats();
                    loadLaws();
                } else {
                    alert(`추가 실패: ${data.오류}`);
                }
            } catch (error) {
                alert(`오류 발생: ${error.message}`);
            }
        }

        // 법령 제거
        async function removeLaw(lawName) {
            if (!confirm(`${lawName}을(를) 제거하시겠습니까?`)) {
                return;
            }

            try {
                const response = await fetch('/api/remove-law', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 법령명: lawName })
                });

                const data = await response.json();

                if (data.성공) {
                    alert(`${lawName}이(가) 제거되었습니다`);
                    loadStats();
                    loadLaws();
                } else {
                    alert(`제거 실패: ${data.오류}`);
                }
            } catch (error) {
                alert(`오류 발생: ${error.message}`);
            }
        }

        // 탭 전환
        function switchTab(tab) {
            // 모든 탭 버튼과 콘텐츠 비활성화
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // 선택된 탭 활성화
            event.target.classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
        }

        // 여러 법령 일괄 추가
        async function bulkAddLaws() {
            const textarea = document.getElementById('bulk-laws-input');
            const lawsText = textarea.value.trim();
            const resultDiv = document.getElementById('bulk-result');

            if (!lawsText) {
                alert('법령을 입력해주세요');
                return;
            }

            resultDiv.innerHTML = '<div class="loading show"><div class="spinner"></div><p>법령 추가 중...</p></div>';

            try {
                const response = await fetch('/api/bulk-add-laws', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 법령목록: lawsText })
                });

                const data = await response.json();

                if (data.성공) {
                    let html = `<div class="result-box result-success">
                        <h3>✅ 일괄 추가 완료!</h3>
                        <p>총 ${data.총개수}개 중 성공: ${data.성공개수}개, 실패: ${data.실패개수}개, 건너뛰기: ${data.건너뛰기개수}개</p>
                    `;

                    if (data.결과.성공.length > 0) {
                        html += '<h4>✅ 추가된 법령:</h4><ul>';
                        data.결과.성공.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    if (data.결과.건너뛰기.length > 0) {
                        html += '<h4>⏭️ 이미 추적 중:</h4><ul>';
                        data.결과.건너뛰기.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    if (data.결과.실패.length > 0) {
                        html += '<h4>❌ 실패:</h4><ul>';
                        data.결과.실패.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    html += '</div>';
                    resultDiv.innerHTML = html;

                    // 입력창 비우기
                    textarea.value = '';

                    // 목록 새로고침
                    loadStats();
                    loadLaws();
                } else {
                    resultDiv.innerHTML = `<div class="result-box result-error">
                        <h3>❌ 오류 발생</h3>
                        <p>${data.오류}</p>
                    </div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result-box result-error">
                    <h3>❌ 오류 발생</h3>
                    <p>${error.message}</p>
                </div>`;
            }
        }

        // 파일 업로드
        async function uploadFile() {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            const resultDiv = document.getElementById('file-result');

            if (!file) {
                alert('파일을 선택해주세요');
                return;
            }

            resultDiv.innerHTML = '<div class="loading show"><div class="spinner"></div><p>파일 업로드 및 법령 추가 중...</p></div>';

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload-file', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.성공) {
                    let html = `<div class="result-box result-success">
                        <h3>✅ 파일 업로드 완료!</h3>
                        <p>총 ${data.총개수}개 중 성공: ${data.성공개수}개, 실패: ${data.실패개수}개, 건너뛰기: ${data.건너뛰기개수}개</p>
                    `;

                    if (data.결과.성공.length > 0) {
                        html += '<h4>✅ 추가된 법령:</h4><ul>';
                        data.결과.성공.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    if (data.결과.건너뛰기.length > 0) {
                        html += '<h4>⏭️ 이미 추적 중:</h4><ul>';
                        data.결과.건너뛰기.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    if (data.결과.실패.length > 0) {
                        html += '<h4>❌ 실패:</h4><ul>';
                        data.결과.실패.forEach(law => {
                            html += `<li class="result-item">${law}</li>`;
                        });
                        html += '</ul>';
                    }

                    html += '</div>';
                    resultDiv.innerHTML = html;

                    // 파일 입력 초기화
                    fileInput.value = '';

                    // 목록 새로고침
                    loadStats();
                    loadLaws();
                } else {
                    resultDiv.innerHTML = `<div class="result-box result-error">
                        <h3>❌ 오류 발생</h3>
                        <p>${data.오류}</p>
                    </div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result-box result-error">
                    <h3>❌ 오류 발생</h3>
                    <p>${error.message}</p>
                </div>`;
            }
        }

        // 새로고침
        function refreshLaws() {
            loadStats();
            loadLaws();
        }
    </script>
</body>
</html>"""

    with open(templates_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)


if __name__ == "__main__":
    # 템플릿 생성
    create_templates()

    if not api_key:
        print("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    else:
        print("="*80)
        print("🌐 법령 추적 웹 대시보드")
        print("="*80)
        print(f"\n🚀 서버 시작: http://localhost:5000")
        print("📌 브라우저에서 위 주소로 접속하세요\n")
        print("종료하려면 Ctrl+C를 누르세요")
        print("="*80 + "\n")

        app.run(debug=True, host='0.0.0.0', port=5000)
