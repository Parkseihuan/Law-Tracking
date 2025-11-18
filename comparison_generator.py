#!/usr/bin/env python3
"""
법령 신구대조표 생성기
"""

import difflib
from typing import List, Tuple
from pathlib import Path
from datetime import datetime


class LawComparisonGenerator:
    """법령 신구대조표 생성 클래스"""

    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def generate_text_comparison(
        self,
        old_content: str,
        new_content: str,
        law_name: str,
        output_file: str = None
    ) -> str:
        """텍스트 형식 신구대조표 생성"""

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{law_name}_신구대조_{timestamp}.txt"

        # Unified diff 생성
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile='개정 전',
            tofile='개정 후',
            lineterm=''
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"법령 신구대조표: {law_name}\n")
            f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            f.write(''.join(diff))

        print(f"✅ 텍스트 신구대조표 생성: {output_file}")
        return str(output_file)

    def generate_html_comparison(
        self,
        old_content: str,
        new_content: str,
        law_name: str,
        output_file: str = None
    ) -> str:
        """HTML 형식 신구대조표 생성"""

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{law_name}_신구대조_{timestamp}.html"

        # HTML diff 생성
        differ = difflib.HtmlDiff(wrapcolumn=60)
        html_diff = differ.make_file(
            old_content.splitlines(),
            new_content.splitlines(),
            fromdesc='개정 전',
            todesc='개정 후',
            context=True,
            numlines=3
        )

        # 한국어 스타일 추가
        styled_html = self._add_korean_style(html_diff, law_name)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        print(f"✅ HTML 신구대조표 생성: {output_file}")
        return str(output_file)

    def _add_korean_style(self, html_content: str, law_name: str) -> str:
        """HTML에 한국어 친화적 스타일 추가"""

        # 헤더 추가
        header = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{law_name} - 신구대조표</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 5px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border: 1px solid #ddd;
            vertical-align: top;
        }}
        .diff_add {{
            background-color: #d4edda;
            color: #155724;
        }}
        .diff_chg {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .diff_sub {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .diff_next {{
            background-color: #e9ecef;
        }}
        .legend {{
            margin: 20px 0;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 {law_name} - 신구대조표</h1>
        <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
    </div>

    <div class="legend">
        <strong>범례:</strong>
        <span class="legend-item diff_add">추가된 내용</span>
        <span class="legend-item diff_chg">변경된 내용</span>
        <span class="legend-item diff_sub">삭제된 내용</span>
    </div>
"""

        # 기존 HTML에서 body 부분만 추출하여 결합
        if '<body>' in html_content:
            body_start = html_content.find('<table')
            body_end = html_content.find('</body>')
            if body_start > 0 and body_end > 0:
                table_content = html_content[body_start:body_end]
                return header + table_content + "\n</body>\n</html>"

        return html_content

    def generate_side_by_side_comparison(
        self,
        old_content: str,
        new_content: str,
        law_name: str,
        output_file: str = None
    ) -> str:
        """좌우 비교 형식 신구대조표 생성"""

        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{law_name}_비교_{timestamp}.html"

        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        # SequenceMatcher로 변경 부분 찾기
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{law_name} - 신구대조표</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 16px;
        }}
        td {{
            padding: 10px;
            border: 1px solid #ddd;
            vertical-align: top;
            width: 50%;
        }}
        .line-number {{
            color: #888;
            font-size: 12px;
            margin-right: 10px;
        }}
        .added {{
            background-color: #d4edda;
        }}
        .removed {{
            background-color: #f8d7da;
        }}
        .changed {{
            background-color: #fff3cd;
        }}
        .unchanged {{
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 {law_name} - 신구대조표</h1>
        <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>개정 전</th>
                <th>개정 후</th>
            </tr>
        </thead>
        <tbody>
"""

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 동일한 부분
                for i in range(i1, i2):
                    line = old_lines[i] if i < len(old_lines) else ""
                    html_content += f"""
            <tr>
                <td class="unchanged"><span class="line-number">{i+1}</span>{self._escape_html(line)}</td>
                <td class="unchanged"><span class="line-number">{j1+i-i1+1}</span>{self._escape_html(line)}</td>
            </tr>
"""
            elif tag == 'delete':
                # 삭제된 부분
                for i in range(i1, i2):
                    line = old_lines[i] if i < len(old_lines) else ""
                    html_content += f"""
            <tr>
                <td class="removed"><span class="line-number">{i+1}</span>{self._escape_html(line)}</td>
                <td class="removed"></td>
            </tr>
"""
            elif tag == 'insert':
                # 추가된 부분
                for j in range(j1, j2):
                    line = new_lines[j] if j < len(new_lines) else ""
                    html_content += f"""
            <tr>
                <td class="added"></td>
                <td class="added"><span class="line-number">{j+1}</span>{self._escape_html(line)}</td>
            </tr>
"""
            elif tag == 'replace':
                # 변경된 부분
                max_lines = max(i2-i1, j2-j1)
                for k in range(max_lines):
                    old_line = old_lines[i1+k] if (i1+k) < i2 else ""
                    new_line = new_lines[j1+k] if (j1+k) < j2 else ""
                    html_content += f"""
            <tr>
                <td class="changed"><span class="line-number">{i1+k+1 if old_line else ''}</span>{self._escape_html(old_line)}</td>
                <td class="changed"><span class="line-number">{j1+k+1 if new_line else ''}</span>{self._escape_html(new_line)}</td>
            </tr>
"""

        html_content += """
        </tbody>
    </table>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 좌우 비교 신구대조표 생성: {output_file}")
        return str(output_file)

    def _escape_html(self, text: str) -> str:
        """HTML 이스케이프"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def demo():
    """데모 실행"""
    generator = LawComparisonGenerator()

    # 예시 데이터
    old_law = """제1조(목적) 이 법은 사립학교의 특수성에 비추어 그 자주성을 확보하고 공공성을 앙양함으로써 사립학교의 건전한 발달을 도모함을 목적으로 한다.

제2조(정의) 이 법에서 사용하는 용어의 정의는 다음과 같다.
1. "학교법인"이라 함은 사립학교를 설치·경영하는 것을 목적으로 이 법에 의하여 설립된 법인을 말한다.
2. "사립학교"라 함은 학교법인이 설치·경영하는 학교를 말한다.

제3조(학교법인) 학교법인은 대학·고등학교를 설치·경영할 수 있다."""

    new_law = """제1조(목적) 이 법은 사립학교의 특수성에 비추어 그 자주성을 확보하고 공공성과 투명성을 강화함으로써 사립학교의 건전한 발달을 도모함을 목적으로 한다.

제2조(정의) 이 법에서 사용하는 용어의 정의는 다음과 같다.
1. "학교법인"이라 함은 사립학교를 설치·경영하는 것을 목적으로 이 법에 의하여 설립된 법인을 말한다.
2. "사립학교"라 함은 학교법인 또는 사인이 설치·경영하는 학교를 말한다.
3. "이사회"라 함은 학교법인의 최고 의사결정기구를 말한다.

제3조(학교법인) 학교법인은 대학·고등학교·중학교를 설치·경영할 수 있다.

제4조(투명성) 학교법인은 경영의 투명성을 확보하여야 한다."""

    print("="*80)
    print("🔍 법령 신구대조표 생성 데모")
    print("="*80)

    # 1. 텍스트 비교
    print("\n1️⃣  텍스트 형식 생성")
    generator.generate_text_comparison(old_law, new_law, "사립학교법")

    # 2. HTML 비교
    print("\n2️⃣  HTML 형식 생성")
    generator.generate_html_comparison(old_law, new_law, "사립학교법")

    # 3. 좌우 비교
    print("\n3️⃣  좌우 비교 형식 생성")
    generator.generate_side_by_side_comparison(old_law, new_law, "사립학교법")

    print("\n✅ 모든 형식의 신구대조표가 생성되었습니다!")
    print(f"📁 출력 디렉토리: {Path('output').absolute()}")


if __name__ == "__main__":
    demo()
