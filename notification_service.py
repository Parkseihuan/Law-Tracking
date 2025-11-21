"""
알림 서비스 모듈
이메일 및 웹훅을 통한 법령 변경 알림
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import requests
from datetime import datetime


class NotificationService:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def send_email_notification(self, subject: str, changes: List[Dict]) -> bool:
        """이메일 알림 발송"""
        email_config = self.config_manager.get_email_config()

        if not email_config.get("enabled"):
            print("이메일 알림이 비활성화되어 있습니다.")
            return False

        if not email_config.get("recipients"):
            print("수신자가 설정되지 않았습니다.")
            return False

        try:
            # HTML 이메일 생성
            html_content = self._generate_email_html(subject, changes)

            # MIME 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = email_config.get("sender", email_config.get("smtp_username"))
            message["To"] = ", ".join(email_config["recipients"])

            # HTML 파트 추가
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["smtp_username"], email_config["smtp_password"])
                server.send_message(message)

            print(f"이메일 알림 발송 완료: {len(email_config['recipients'])}명")
            return True

        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False

    def _generate_email_html(self, subject: str, changes: List[Dict]) -> str:
        """이메일 HTML 생성"""
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .law-item {{ background: white; padding: 20px; margin-bottom: 15px;
                           border-radius: 8px; border-left: 4px solid #667eea; }}
                .law-name {{ font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
                .law-detail {{ color: #666; font-size: 14px; margin: 5px 0; }}
                .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px;
                        font-size: 12px; font-weight: bold; }}
                .badge-new {{ background: #28a745; color: white; }}
                .badge-updated {{ background: #ffc107; color: #000; }}
                .badge-deleted {{ background: #dc3545; color: white; }}
                .footer {{ text-align: center; color: #999; margin-top: 30px; padding-top: 20px;
                         border-top: 1px solid #ddd; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ text-align: center; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚖️ {subject}</h1>
                    <p>📅 {current_time}</p>
                </div>
                <div class="content">
        """

        if not changes:
            html += """
                    <p style="text-align: center; color: #666; padding: 40px;">
                        ✅ 변경사항이 없습니다.
                    </p>
            """
        else:
            # 통계 추가
            new_count = sum(1 for c in changes if c.get("type") == "new")
            updated_count = sum(1 for c in changes if c.get("type") == "updated")
            deleted_count = sum(1 for c in changes if c.get("type") == "deleted")

            html += f"""
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{new_count}</div>
                            <div class="stat-label">신규</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{updated_count}</div>
                            <div class="stat-label">개정</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{deleted_count}</div>
                            <div class="stat-label">폐지</div>
                        </div>
                    </div>
            """

            # 변경사항 목록
            for change in changes:
                law_name = change.get("법령명", "알 수 없음")
                change_type = change.get("type", "updated")
                change_count = change.get("변경횟수", 0)
                last_check = change.get("마지막확인", "-")

                badge_class = {
                    "new": "badge-new",
                    "updated": "badge-updated",
                    "deleted": "badge-deleted"
                }.get(change_type, "badge-updated")

                badge_text = {
                    "new": "신규",
                    "updated": "개정",
                    "deleted": "폐지"
                }.get(change_type, "변경")

                html += f"""
                    <div class="law-item">
                        <div class="law-name">
                            {law_name}
                            <span class="badge {badge_class}">{badge_text}</span>
                        </div>
                        <div class="law-detail">📊 변경 횟수: {change_count}건</div>
                        <div class="law-detail">🕐 마지막 확인: {last_check}</div>
                    </div>
                """

        html += """
                </div>
                <div class="footer">
                    <p>이 이메일은 법령 추적 시스템에서 자동으로 발송되었습니다.</p>
                    <p>문의사항이 있으시면 시스템 관리자에게 연락해주세요.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def send_discord_notification(self, changes: List[Dict]) -> bool:
        """Discord 웹훅 알림 발송"""
        discord_config = self.config_manager.get("notifications.discord", {})

        if not discord_config.get("enabled"):
            print("Discord 알림이 비활성화되어 있습니다.")
            return False

        webhook_url = discord_config.get("webhook_url")
        if not webhook_url:
            print("Discord 웹훅 URL이 설정되지 않았습니다.")
            return False

        try:
            # 통계 계산
            new_count = sum(1 for c in changes if c.get("type") == "new")
            updated_count = sum(1 for c in changes if c.get("type") == "updated")
            deleted_count = sum(1 for c in changes if c.get("type") == "deleted")

            # Discord Embed 생성
            embed = {
                "title": "⚖️ 법령 변경 알림",
                "description": f"총 **{len(changes)}건**의 변경사항이 발견되었습니다.",
                "color": 0x667eea,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {"name": "🆕 신규", "value": str(new_count), "inline": True},
                    {"name": "📝 개정", "value": str(updated_count), "inline": True},
                    {"name": "❌ 폐지", "value": str(deleted_count), "inline": True}
                ],
                "footer": {"text": "법령 추적 시스템"}
            }

            # 변경사항 목록 추가 (최대 5개)
            if changes:
                laws_text = ""
                for i, change in enumerate(changes[:5]):
                    law_name = change.get("법령명", "알 수 없음")
                    change_count = change.get("변경횟수", 0)
                    laws_text += f"• **{law_name}** ({change_count}건)\n"

                if len(changes) > 5:
                    laws_text += f"\n... 외 {len(changes) - 5}건"

                embed["fields"].append({
                    "name": "변경된 법령",
                    "value": laws_text,
                    "inline": False
                })

            payload = {
                "username": "법령 추적 시스템",
                "embeds": [embed]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            print(f"Discord 알림 발송 완료")
            return True

        except Exception as e:
            print(f"Discord 발송 실패: {e}")
            return False

    def send_telegram_notification(self, changes: List[Dict]) -> bool:
        """Telegram Bot 알림 발송"""
        telegram_config = self.config_manager.get("notifications.telegram", {})

        if not telegram_config.get("enabled"):
            print("Telegram 알림이 비활성화되어 있습니다.")
            return False

        bot_token = telegram_config.get("bot_token")
        chat_id = telegram_config.get("chat_id")

        if not bot_token or not chat_id:
            print("Telegram Bot 토큰 또는 Chat ID가 설정되지 않았습니다.")
            return False

        try:
            # 통계 계산
            new_count = sum(1 for c in changes if c.get("type") == "new")
            updated_count = sum(1 for c in changes if c.get("type") == "updated")
            deleted_count = sum(1 for c in changes if c.get("type") == "deleted")

            # Telegram 메시지 생성 (Markdown 형식)
            message = f"⚖️ *법령 변경 알림*\n\n"
            message += f"총 *{len(changes)}건*의 변경사항이 발견되었습니다.\n\n"
            message += f"🆕 신규: {new_count}건\n"
            message += f"📝 개정: {updated_count}건\n"
            message += f"❌ 폐지: {deleted_count}건\n\n"

            # 변경사항 목록 (최대 10개)
            if changes:
                message += "*변경된 법령:*\n"
                for i, change in enumerate(changes[:10]):
                    law_name = change.get("법령명", "알 수 없음")
                    change_count = change.get("변경횟수", 0)
                    message += f"• {law_name} ({change_count}건)\n"

                if len(changes) > 10:
                    message += f"\n... 외 {len(changes) - 10}건"

            message += f"\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Telegram API 호출
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            print(f"Telegram 알림 발송 완료")
            return True

        except Exception as e:
            print(f"Telegram 발송 실패: {e}")
            return False

    def send_slack_notification(self, changes: List[Dict]) -> bool:
        """Slack 웹훅 알림 발송"""
        slack_config = self.config_manager.get("notifications.slack", {})

        if not slack_config.get("enabled"):
            print("Slack 알림이 비활성화되어 있습니다.")
            return False

        webhook_url = slack_config.get("webhook_url")
        if not webhook_url:
            print("Slack 웹훅 URL이 설정되지 않았습니다.")
            return False

        try:
            # 통계 계산
            new_count = sum(1 for c in changes if c.get("type") == "new")
            updated_count = sum(1 for c in changes if c.get("type") == "updated")
            deleted_count = sum(1 for c in changes if c.get("type") == "deleted")

            # Slack Block Kit 메시지 생성
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚖️ 법령 변경 알림"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"총 *{len(changes)}건*의 변경사항이 발견되었습니다."
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*🆕 신규*\n{new_count}건"},
                        {"type": "mrkdwn", "text": f"*📝 개정*\n{updated_count}건"},
                        {"type": "mrkdwn", "text": f"*❌ 폐지*\n{deleted_count}건"},
                        {"type": "mrkdwn", "text": f"*📅 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                    ]
                }
            ]

            # 변경사항 목록 추가 (최대 5개)
            if changes:
                laws_text = ""
                for i, change in enumerate(changes[:5]):
                    law_name = change.get("법령명", "알 수 없음")
                    change_count = change.get("변경횟수", 0)
                    laws_text += f"• *{law_name}* ({change_count}건)\n"

                if len(changes) > 5:
                    laws_text += f"\n... 외 {len(changes) - 5}건"

                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*변경된 법령:*\n{laws_text}"
                    }
                })

            payload = {"blocks": blocks}

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            print(f"Slack 알림 발송 완료")
            return True

        except Exception as e:
            print(f"Slack 발송 실패: {e}")
            return False

    def send_webhook_notification(self, changes: List[Dict]) -> bool:
        """웹훅 알림 발송 (범용)"""
        webhook_config = self.config_manager.get("notifications.webhook", {})

        if not webhook_config.get("enabled"):
            print("웹훅 알림이 비활성화되어 있습니다.")
            return False

        webhook_url = webhook_config.get("url")
        if not webhook_url:
            print("웹훅 URL이 설정되지 않았습니다.")
            return False

        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "changes": changes,
                "summary": {
                    "total": len(changes),
                    "new": sum(1 for c in changes if c.get("type") == "new"),
                    "updated": sum(1 for c in changes if c.get("type") == "updated"),
                    "deleted": sum(1 for c in changes if c.get("type") == "deleted")
                }
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            print(f"웹훅 알림 발송 완료: {webhook_url}")
            return True

        except Exception as e:
            print(f"웹훅 발송 실패: {e}")
            return False

    def notify_changes(self, changes: List[Dict]) -> Dict[str, bool]:
        """모든 활성화된 알림 채널로 변경사항 전송"""
        results = {}

        # Discord 알림
        if self.config_manager.get("notifications.discord.enabled"):
            results["discord"] = self.send_discord_notification(changes)

        # Telegram 알림
        if self.config_manager.get("notifications.telegram.enabled"):
            results["telegram"] = self.send_telegram_notification(changes)

        # Slack 알림
        if self.config_manager.get("notifications.slack.enabled"):
            results["slack"] = self.send_slack_notification(changes)

        # 이메일 알림
        if self.config_manager.get("notifications.email.enabled"):
            subject = f"⚖️ 법령 변경 알림 ({len(changes)}건)"
            results["email"] = self.send_email_notification(subject, changes)

        # 웹훅 알림
        if self.config_manager.get("notifications.webhook.enabled"):
            results["webhook"] = self.send_webhook_notification(changes)

        return results

    def test_email_connection(self) -> Dict[str, any]:
        """이메일 연결 테스트"""
        email_config = self.config_manager.get_email_config()

        if not email_config.get("smtp_server"):
            return {"success": False, "message": "SMTP 서버가 설정되지 않았습니다."}

        try:
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"], timeout=10) as server:
                server.starttls()
                server.login(email_config["smtp_username"], email_config["smtp_password"])

            return {"success": True, "message": "이메일 서버 연결 성공"}

        except smtplib.SMTPAuthenticationError:
            return {"success": False, "message": "인증 실패: 사용자명 또는 비밀번호를 확인하세요."}
        except smtplib.SMTPException as e:
            return {"success": False, "message": f"SMTP 오류: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"연결 실패: {str(e)}"}
