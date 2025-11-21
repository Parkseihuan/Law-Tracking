"""
설정 관리 모듈
스케줄 설정, 알림 설정 등을 JSON 파일로 저장/로드
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    def __init__(self, config_file: str = "law_tracker_config.json"):
        self.config_file = config_file
        self.default_config = {
            "schedule": {
                "enabled": False,
                "cron": "0 9 * * *",  # 매일 오전 9시 (cron 형식)
                "timezone": "Asia/Seoul",
                "last_run": None
            },
            "notifications": {
                "discord": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": ""
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "email": {
                    "enabled": False,
                    "recipients": [],
                    "smtp_server": "",
                    "smtp_port": 587,
                    "smtp_username": "",
                    "smtp_password": "",
                    "sender": ""
                },
                "webhook": {
                    "enabled": False,
                    "url": ""
                }
            },
            "api": {
                "key": "psh@yi.ac.kr",
                "base_url": "https://www.law.go.kr/DRF/lawSearch.do"
            },
            "tracking": {
                "auto_add_related": False,
                "max_depth": 2
            }
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 기본 설정과 병합 (새로운 설정 키가 추가될 수 있음)
                    return self._merge_configs(self.default_config, loaded_config)
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")
                return self.default_config.copy()
        else:
            # 기본 설정으로 파일 생성
            self.save_config(self.default_config)
            return self.default_config.copy()

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """기본 설정과 로드된 설정 병합"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def save_config(self, config: Optional[Dict] = None) -> bool:
        """설정 파일 저장"""
        try:
            if config is not None:
                self.config = config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """설정 값 가져오기 (점 표기법 지원: 'schedule.enabled')"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any, save: bool = True) -> bool:
        """설정 값 설정 (점 표기법 지원)"""
        keys = key_path.split('.')
        config = self.config

        # 마지막 키 전까지 탐색
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # 마지막 키에 값 설정
        config[keys[-1]] = value

        if save:
            return self.save_config()
        return True

    def get_schedule_config(self) -> Dict:
        """스케줄 설정 가져오기"""
        return self.config.get("schedule", {})

    def update_schedule_config(self, enabled: bool = None, cron: str = None,
                              timezone: str = None) -> bool:
        """스케줄 설정 업데이트"""
        schedule = self.config.get("schedule", {})

        if enabled is not None:
            schedule["enabled"] = enabled
        if cron is not None:
            schedule["cron"] = cron
        if timezone is not None:
            schedule["timezone"] = timezone

        self.config["schedule"] = schedule
        return self.save_config()

    def update_last_run(self, timestamp: str = None) -> bool:
        """마지막 실행 시간 업데이트"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        return self.set("schedule.last_run", timestamp)

    def get_email_config(self) -> Dict:
        """이메일 알림 설정 가져오기"""
        return self.config.get("notifications", {}).get("email", {})

    def update_email_config(self, enabled: bool = None, recipients: list = None,
                           smtp_server: str = None, smtp_port: int = None,
                           smtp_username: str = None, smtp_password: str = None,
                           sender: str = None) -> bool:
        """이메일 알림 설정 업데이트"""
        email = self.get_email_config()

        if enabled is not None:
            email["enabled"] = enabled
        if recipients is not None:
            email["recipients"] = recipients
        if smtp_server is not None:
            email["smtp_server"] = smtp_server
        if smtp_port is not None:
            email["smtp_port"] = smtp_port
        if smtp_username is not None:
            email["smtp_username"] = smtp_username
        if smtp_password is not None:
            email["smtp_password"] = smtp_password
        if sender is not None:
            email["sender"] = sender

        if "notifications" not in self.config:
            self.config["notifications"] = {}
        self.config["notifications"]["email"] = email
        return self.save_config()

    def get_all_config(self) -> Dict:
        """전체 설정 가져오기"""
        return self.config.copy()
