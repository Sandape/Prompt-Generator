import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import User, LoginLog, Project, ProjectCreate, ProjectUpdate, AIConfig, AIConfigCreate, AIConfigUpdate

class JSONStorage:
    """JSON存储管理器"""

    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.ai_configs_file = os.path.join(self.data_dir, "ai_configs.json")
        self.logs_dir = "logs"
        self.login_log_file = os.path.join(self.logs_dir, "login.log")

        # 创建必要的目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # 初始化用户文件
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 初始化项目文件
        if not os.path.exists(self.projects_file):
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        # 初始化AI配置文件
        if not os.path.exists(self.ai_configs_file):
            with open(self.ai_configs_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def _load_users(self) -> List[dict]:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_users(self, users: List[dict]):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False, default=str)

    def _load_projects(self) -> List[dict]:
        """加载项目数据"""
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_projects(self, projects: List[dict]):
        """保存项目数据"""
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False, default=str)

    def _convert_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换项目数据，确保日期字段正确格式化"""
        converted_data = project_data.copy()

        # 转换日期字符串为datetime对象
        if 'created_at' in converted_data and isinstance(converted_data['created_at'], str):
            try:
                converted_data['created_at'] = datetime.fromisoformat(converted_data['created_at'].replace(' ', 'T'))
            except ValueError:
                # 如果转换失败，尝试其他格式
                try:
                    converted_data['created_at'] = datetime.strptime(converted_data['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    # 如果还是失败，使用当前时间
                    converted_data['created_at'] = datetime.now()

        if 'updated_at' in converted_data and isinstance(converted_data['updated_at'], str):
            try:
                converted_data['updated_at'] = datetime.fromisoformat(converted_data['updated_at'].replace(' ', 'T'))
            except ValueError:
                try:
                    converted_data['updated_at'] = datetime.strptime(converted_data['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    converted_data['updated_at'] = datetime.now()

        return converted_data

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        users = self._load_users()
        for user_data in users:
            if user_data['email'] == email:
                return User(**user_data)
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        users = self._load_users()
        for user_data in users:
            if user_data['username'] == username:
                return User(**user_data)
        return None

    def create_user(self, user: User) -> User:
        """创建新用户"""
        users = self._load_users()

        # 获取下一个ID
        max_id = max([u.get('id', 0) for u in users], default=0)
        user.id = max_id + 1
        user.created_at = datetime.now()

        users.append(user.dict())
        self._save_users(users)
        return user

    def log_login(self, email: str, username: str, ip_address: str = None, user_agent: str = None):
        """记录登录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Login - Email: {email}, Username: {username}"

        if ip_address:
            log_entry += f", IP: {ip_address}"
        if user_agent:
            log_entry += f", User-Agent: {user_agent[:100]}"  # 截断过长的User-Agent

        log_entry += "\n"

        with open(self.login_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    # 项目管理方法
    def get_projects_by_user_id(self, user_id: int) -> List[Project]:
        """获取用户的项目列表"""
        projects = self._load_projects()
        user_projects = []
        for project_data in projects:
            if project_data['user_id'] == user_id:
                converted_data = self._convert_project_data(project_data)
                user_projects.append(Project(**converted_data))
        return user_projects

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """通过ID获取项目"""
        projects = self._load_projects()
        for project_data in projects:
            if project_data['id'] == project_id:
                converted_data = self._convert_project_data(project_data)
                return Project(**converted_data)
        return None

    def create_project(self, user_id: int, project_data: ProjectCreate) -> Project:
        """创建新项目"""
        projects = self._load_projects()

        # 检查用户项目数量限制
        user_projects = [p for p in projects if p['user_id'] == user_id]
        if len(user_projects) >= 5:
            raise ValueError("每个用户最多只能创建5个项目")

        # 获取下一个ID
        max_id = max([p.get('id', 0) for p in projects], default=0)
        project_id = max_id + 1

        now = datetime.now()
        project = Project(
            id=project_id,
            user_id=user_id,
            name=project_data.name,
            development_standard=project_data.development_standard,
            interface_example=project_data.interface_example,
            entity_example=project_data.entity_example,
            mapper_example=project_data.mapper_example,
            created_at=now,
            updated_at=now
        )

        projects.append(project.dict())
        self._save_projects(projects)
        return project

    def update_project(self, project_id: int, update_data: ProjectUpdate) -> Optional[Project]:
        """更新项目信息"""
        projects = self._load_projects()

        for i, project_data in enumerate(projects):
            if project_data['id'] == project_id:
                # 更新提供的数据
                update_dict = update_data.dict(exclude_unset=True)
                if update_dict:
                    projects[i].update(update_dict)
                    projects[i]['updated_at'] = datetime.now().isoformat()

                self._save_projects(projects)
                converted_data = self._convert_project_data(projects[i])
                return Project(**converted_data)

        return None

    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        projects = self._load_projects()

        for i, project_data in enumerate(projects):
            if project_data['id'] == project_id:
                del projects[i]
                self._save_projects(projects)
                return True

        return False

    def can_create_project(self, user_id: int) -> bool:
        """检查用户是否可以创建新项目"""
        user_projects = self.get_projects_by_user_id(user_id)
        return len(user_projects) < 5

    def _load_ai_configs(self) -> List[dict]:
        """加载AI配置数据"""
        try:
            with open(self.ai_configs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_ai_configs(self, ai_configs: List[dict]):
        """保存AI配置数据"""
        with open(self.ai_configs_file, 'w', encoding='utf-8') as f:
            json.dump(ai_configs, f, indent=2, ensure_ascii=False, default=str)

    def _convert_ai_config_data(self, ai_config_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换AI配置数据，确保日期字段正确格式化"""
        converted_data = ai_config_data.copy()

        # 转换日期字符串为datetime对象
        if 'created_at' in converted_data and isinstance(converted_data['created_at'], str):
            try:
                converted_data['created_at'] = datetime.fromisoformat(converted_data['created_at'].replace(' ', 'T'))
            except ValueError:
                try:
                    converted_data['created_at'] = datetime.strptime(converted_data['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    converted_data['created_at'] = datetime.now()

        if 'updated_at' in converted_data and isinstance(converted_data['updated_at'], str):
            try:
                converted_data['updated_at'] = datetime.fromisoformat(converted_data['updated_at'].replace(' ', 'T'))
            except ValueError:
                try:
                    converted_data['updated_at'] = datetime.strptime(converted_data['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    converted_data['updated_at'] = datetime.now()

        return converted_data

    def get_ai_config_by_user_id(self, user_id: int) -> Optional[AIConfig]:
        """通过用户ID获取AI配置"""
        ai_configs = self._load_ai_configs()
        for ai_config_data in ai_configs:
            if ai_config_data['user_id'] == user_id:
                converted_data = self._convert_ai_config_data(ai_config_data)
                return AIConfig(**converted_data)
        return None

    def create_ai_config(self, user_id: int, ai_config_data: AIConfigCreate) -> AIConfig:
        """创建AI配置"""
        ai_configs = self._load_ai_configs()

        # 检查用户是否已有AI配置
        for config in ai_configs:
            if config['user_id'] == user_id:
                raise ValueError("用户已存在AI配置")

        # 获取下一个ID
        max_id = max([c.get('id', 0) for c in ai_configs], default=0)
        ai_config_id = max_id + 1

        now = datetime.now()
        ai_config = AIConfig(
            id=ai_config_id,
            user_id=user_id,
            api_key=ai_config_data.api_key,
            api_url=ai_config_data.api_url,
            model_name=ai_config_data.model_name,
            created_at=now,
            updated_at=now
        )

        ai_configs.append(ai_config.dict())
        self._save_ai_configs(ai_configs)
        return ai_config

    def update_ai_config(self, user_id: int, update_data: AIConfigUpdate) -> Optional[AIConfig]:
        """更新AI配置"""
        ai_configs = self._load_ai_configs()

        for i, ai_config_data in enumerate(ai_configs):
            if ai_config_data['user_id'] == user_id:
                # 更新提供的数据
                update_dict = update_data.dict(exclude_unset=True)
                if update_dict:
                    ai_configs[i].update(update_dict)
                    ai_configs[i]['updated_at'] = datetime.now().isoformat()

                self._save_ai_configs(ai_configs)
                converted_data = self._convert_ai_config_data(ai_configs[i])
                return AIConfig(**converted_data)

        return None

    def delete_ai_config(self, user_id: int) -> bool:
        """删除AI配置"""
        ai_configs = self._load_ai_configs()

        for i, ai_config_data in enumerate(ai_configs):
            if ai_config_data['user_id'] == user_id:
                del ai_configs[i]
                self._save_ai_configs(ai_configs)
                return True

        return False

# 创建全局存储实例
storage = JSONStorage()
