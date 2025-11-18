#!/usr/bin/env python3
"""
법령 개정 알림 시스템
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime
import json


class NotificationSystem:
    """알림 시스템 클래스"""

    def __init__(self, notification_config: Dict = None):
        """
        Args:
            notification_config: 알림 설정
                {
                    "email": {
                        "enabled": True,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "sender": "your_email@gmail.com",
                        "password": "your_app_password",
                        "recipients": ["recipient@example.com"]
                    },
                    "slack": {
                        "enabled": False,
                        "webhook_url": "https://hooks.slack.com/..."
                    }
                }
        """
        self.config = notification_config or self._load_default_config()

    def _load_default_config(self) -> Dict:
        """기본 설정 로드"""
        config_file = "notification_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "email": {"enabled": False},
            "slack": {"enabled": False},
            "telegram": {"enabled": False}
        }

    def notify_law_changes(self, updates: List[Dict]):
        """법령 변경 알림 발송"""
        if not updates:
            print("📭 변경사항 없음 - 알림 생략")
            return

        print(f"\n🔔 {len(updates)}개 법령 변경 - 알림 발송 시작")

        # 이메일 알림
        if self.config.get("email", {}).get("enabled"):
            self._send_email_notification(updates)

        # Slack 알림
        if self.config.get("slack", {}).get("enabled"):
            self._send_slack_notification(updates)

        # Telegram 알림
        if self.config.get("telegram", {}).get("enabled"):
            self._send_telegram_notification(updates)

    def _send_email_notification(self, updates: List[Dict]):
        """이메일 알림 발송"""
        try:
            email_config = self.config["email"]

            # 메시지 구성
            subject = f"[법령 개정 알림] {len(updates)}개 법령이 개정되었습니다"
            body = self._create_email_body(updates)

            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html', 'utf-8'))

            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender'], email_config['password'])
                server.send_message(msg)

            print(f"   ✅ 이메일 발송 완료: {', '.join(email_config['recipients'])}")

        except Exception as e:
            print(f"   ❌ 이메일 발송 실패: {e}")

    def _create_email_body(self, updates: List[Dict]) -> str:
        """이메일 본문 생성 (HTML)"""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 20px;
        }}
        .law-item {{
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f8f9fa;
        }}
        .law-name {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .detail {{
            font-size: 14px;
            color: #555;
            margin: 5px 0;
        }}
        .footer {{
            background-color: #ecf0f1;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 법령 개정 알림</h1>
            <p>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
        </div>

        <div class="content">
            <p><strong>{len(updates)}개의 법령</strong>에 변경사항이 발생했습니다:</p>
"""

        for i, update in enumerate(updates, 1):
            html += f"""
            <div class="law-item">
                <div class="law-name">{i}. {update['법령명']}</div>
                <div class="detail">📅 이전 공포일자: {update['이전공포일자']}</div>
                <div class="detail">📅 현재 공포일자: {update['현재공포일자']}</div>
                <div class="detail">🔢 이전 법령일련번호: {update['이전법령일련번호']}</div>
                <div class="detail">🔢 현재 법령일련번호: {update['현재법령일련번호']}</div>
                <div class="detail">🕐 확인일시: {update['확인일시']}</div>
            </div>
"""

        html += """
        </div>

        <div class="footer">
            <p>법령 추적 시스템 | 자동 발송 메일입니다</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _send_slack_notification(self, updates: List[Dict]):
        """Slack 알림 발송"""
        try:
            import requests

            webhook_url = self.config["slack"]["webhook_url"]

            message = {
                "text": f"🔔 법령 개정 알림 ({len(updates)}건)",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🔔 법령 개정 알림 ({len(updates)}건)"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}*\n다음 법령에 변경사항이 발생했습니다:"
                        }
                    }
                ]
            }

            for update in updates:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📋 {update['법령명']}*\n"
                                f"• 이전: {update['이전공포일자']} (번호: {update['이전법령일련번호']})\n"
                                f"• 현재: {update['현재공포일자']} (번호: {update['현재법령일련번호']})"
                    }
                })

            response = requests.post(webhook_url, json=message)
            if response.status_code == 200:
                print(f"   ✅ Slack 알림 발송 완료")
            else:
                print(f"   ❌ Slack 알림 실패: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Slack 알림 실패: {e}")

    def _send_telegram_notification(self, updates: List[Dict]):
        """Telegram 알림 발송"""
        try:
            import requests

            telegram_config = self.config["telegram"]
            bot_token = telegram_config["bot_token"]
            chat_id = telegram_config["chat_id"]

            message = f"🔔 *법령 개정 알림* ({len(updates)}건)\n\n"
            message += f"_{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}_\n\n"

            for i, update in enumerate(updates, 1):
                message += f"{i}. *{update['법령명']}*\n"
                message += f"   • 이전: {update['이전공포일자']}\n"
                message += f"   • 현재: {update['현재공포일자']}\n\n"

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, data=data)
            if response.status_code == 200:
                print(f"   ✅ Telegram 알림 발송 완료")
            else:
                print(f"   ❌ Telegram 알림 실패: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Telegram 알림 실패: {e}")


def create_notification_config():
    """알림 설정 파일 생성 도우미"""
    print("="*80)
    print("📧 알림 설정 파일 생성")
    print("="*80)

    config = {}

    # 이메일 설정
    print("\n[이메일 알림 설정]")
    email_enabled = input("이메일 알림을 사용하시겠습니까? (y/n): ").lower() == 'y'

    if email_enabled:
        config["email"] = {
            "enabled": True,
            "smtp_server": input("SMTP 서버 (예: smtp.gmail.com): ") or "smtp.gmail.com",
            "smtp_port": int(input("SMTP 포트 (예: 587): ") or "587"),
            "sender": input("발신 이메일: "),
            "password": input("앱 비밀번호: "),
            "recipients": input("수신 이메일 (쉼표로 구분): ").split(',')
        }
    else:
        config["email"] = {"enabled": False}

    # Slack 설정
    print("\n[Slack 알림 설정]")
    slack_enabled = input("Slack 알림을 사용하시겠습니까? (y/n): ").lower() == 'y'

    if slack_enabled:
        config["slack"] = {
            "enabled": True,
            "webhook_url": input("Slack Webhook URL: ")
        }
    else:
        config["slack"] = {"enabled": False}

    # Telegram 설정
    print("\n[Telegram 알림 설정]")
    telegram_enabled = input("Telegram 알림을 사용하시겠습니까? (y/n): ").lower() == 'y'

    if telegram_enabled:
        config["telegram"] = {
            "enabled": True,
            "bot_token": input("Telegram Bot Token: "),
            "chat_id": input("Telegram Chat ID: ")
        }
    else:
        config["telegram"] = {"enabled": False}

    # 파일 저장
    with open('notification_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n✅ 알림 설정이 notification_config.json에 저장되었습니다!")


if __name__ == "__main__":
    # 설정 파일 생성 도우미 실행
    create_notification_config()

    # 테스트 알림
    print("\n[테스트 알림 발송]")
    test = input("테스트 알림을 발송하시겠습니까? (y/n): ").lower() == 'y'

    if test:
        notifier = NotificationSystem()
        test_updates = [{
            "법령명": "사립학교법",
            "이전공포일자": "20250814",
            "현재공포일자": "20250920",
            "이전법령일련번호": "273349",
            "현재법령일련번호": "273500",
            "확인일시": datetime.now().isoformat()
        }]
        notifier.notify_law_changes(test_updates)
