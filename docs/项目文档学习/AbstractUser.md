# Django AbstractUser 详解

## 1. AbstractUser 简介

`AbstractUser` 是 Django 认证系统中的核心类，作为 Django 默认用户模型 `User` 的基类，它提供了完整的用户认证功能。这包括用户名、密码、邮箱、权限等基本字段和方法，同时允许开发者通过继承它来**自定义用户模型**。`AbstractUser` 继承自 `AbstractBaseUser` 和 `PermissionsMixin`，前者提供了核心的认证功能，后者则负责权限管理功能。

## 2. AbstractUser 的默认字段

`AbstractUser` 包含以下默认字段：

| 字段名         | 类型            | 说明             |
| -------------- | --------------- | ---------------- |
| `username`     | `CharField`     | 用户名，唯一     |
| `first_name`   | `CharField`     | 名字             |
| `last_name`    | `CharField`     | 姓氏             |
| `email`        | `EmailField`    | 电子邮箱         |
| `password`     | `CharField`     | 密码（加密存储） |
| `is_active`    | `BooleanField`  | 是否激活         |
| `is_staff`     | `BooleanField`  | 是否为管理员     |
| `is_superuser` | `BooleanField`  | 是否为超级管理员 |
| `date_joined`  | `DateTimeField` | 注册日期         |
| `last_login`   | `DateTimeField` | 最后登录时间     |

## 3. 为什么使用 AbstractUser

使用 `AbstractUser` 自定义用户模型具有以下优势：

- **保留 Django 认证系统的所有功能**：包括登录、注销、密码重置等。
- **可以添加自定义字段**：扩展用户信息，例如手机号、头像等。
- **可以修改默认行为**：例如更改用户名的唯一性验证规则。
- **与 Django admin 无缝集成**：自定义用户模型可以直接在 admin 中使用。

## 4. 校园云宝项目中的 User 模型

在校园云宝项目中，我们通过继承 `AbstractUser` 创建了自定义的 `User` 模型：

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    自定义用户模型
    """
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="电话号码")
    avatar = models.URLField(blank=True, null=True, verbose_name="头像URL")
    bio = models.TextField(blank=True, null=True, verbose_name="个人简介")
    is_verified = models.BooleanField(default=False, verbose_name="是否已验证")
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="学号")
    university = models.CharField(max_length=100, blank=True, null=True, verbose_name="学校")
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name="专业")
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name="年级")
    total_focus_time = models.IntegerField(default=0, verbose_name="总专注时长(分钟)")
    total_savings = models.FloatField(default=0.0, verbose_name="总存钱金额")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        db_table = "user"

    def __str__(self):
        return self.username
```

### 4.1 扩展字段说明

我们在 `AbstractUser` 的基础上添加了以下字段：

| 字段名             | 类型           | 说明             |
| ------------------ | -------------- | ---------------- |
| `phone`            | `CharField`    | 用户电话号码     |
| `avatar`           | `URLField`     | 用户头像URL      |
| `bio`              | `TextField`    | 用户个人简介     |
| `is_verified`      | `BooleanField` | 用户是否已验证   |
| `student_id`       | `CharField`    | 学生学号         |
| `university`       | `CharField`    | 所在学校         |
| `major`            | `CharField`    | 专业             |
| `grade`            | `CharField`    | 年级             |
| `total_focus_time` | `IntegerField` | 总专注时长(分钟) |
| `total_savings`    | `FloatField`   | 总存钱金额       |

这些扩展字段使我们的用户模型更适合校园场景，能够存储学生特有的信息，如学号、学校、专业等，同时也支持应用的核心功能，如记录专注时长和存钱金额。

### 4.2 Meta 配置

```python
class Meta:
    verbose_name = "用户"
    verbose_name_plural = verbose_name
    db_table = "user"
```

- `verbose_name`：模型在 admin 界面中显示的名称。
- `verbose_name_plural`：模型的复数名称，这里设置为与单数形式相同。
- `db_table`：数据库表名，这里设置为 `"user"`。

## 5. 在项目中使用自定义用户模型

要使用自定义的用户模型，需要在 `settings.py` 中设置 `AUTH_USER_MODEL`：

```python
AUTH_USER_MODEL = 'user.User'
```

这告诉 Django 使用我们的自定义用户模型，而不是默认的 `auth.User`。

## 6. 自定义用户模型的最佳实践

- **在项目开始时就创建自定义用户模型**：即使一开始不需要额外的字段，也建议创建自定义用户模型，因为后期修改会很复杂。
- **使用 `get_user_model()`**：在代码中引用用户模型时，使用 `django.contrib.auth.get_user_model()` 而不是直接导入模型类。
- **在外键关系中使用 `settings.AUTH_USER_MODEL`**：例如 `models.ForeignKey(settings.AUTH_USER_MODEL, ...)`。
- **保持用户名和邮箱的唯一性**：确保用户可以通过唯一标识符登录。
- **考虑密码安全**：使用 Django 提供的密码验证器确保密码强度。

## 7. 与 Django REST Framework 集成

在校园云宝项目中，我们使用 Django REST Framework 创建了用户相关的 API：

- 用户注册：`/user/register`
- 用户登录：`/user/login`
- 用户登出：`/user/logout`
- 用户信息：`/user/profile`

这些 API 使用了自定义的序列化器来处理用户数据：

- `UserRegisterSerializer`：处理用户注册。
- `UserLoginSerializer`：处理用户登录。
- `UserProfileSerializer`：处理用户信息获取。
- `UserUpdateSerializer`：处理用户信息更新。

## 8. 用户模型的应用场景

在校园云宝项目中，自定义用户模型的应用场景包括：

- **个人提升模块**：记录用户的专注时长和存钱金额。
- **校园规划模块**：根据用户的学校、专业等信息提供个性化的规划建议。
- **虚拟自习室模块**：用户可以加入自习室，记录学习时间。
- **生活助手模块**：根据用户的位置和偏好提供生活服务。

## 9. 用户模型的迁移

当修改用户模型时，需要创建和应用数据库迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

在 `apps.py` 中，我们为用户应用配置了应用名称和显示名称：

```python
from django.apps import AppConfig

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user'
    verbose_name = '用户管理'
```

## 10. 总结

Django 的 `AbstractUser` 提供了一种灵活的方式来定制用户模型，同时保留了 Django 认证系统的所有功能。在校园云宝项目中，我们通过继承 `AbstractUser` 并添加额外字段，创建了一个适合校园场景的用户模型，支持存储学生特有的信息和应用核心功能数据。通过合理设计用户模型和相关 API，我们为校园云宝应用提供了完善的用户管理功能，包括注册、登录、信息管理等，为其他功能模块提供了坚实的基础。
