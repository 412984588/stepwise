# Beta 邀请码管理工具

这套工具用于管理 StepWise Private Beta 的邀请码系统。

## 📂 文件说明

| 文件                     | 用途                         |
| ------------------------ | ---------------------------- |
| `generate_beta_codes.py` | 生成批量邀请码               |
| `verify_beta_code.py`    | 验证邀请码有效性             |
| `beta_stats.py`          | 查看使用统计                 |
| `beta_codes.csv`         | 邀请码数据库（不提交到 Git） |

## 🔐 生成邀请码

### 基础用法

```bash
# 生成 100 个邀请码
python3 scripts/generate_beta_codes.py -n 100 -o beta_codes.csv
```

### 高级选项

```bash
# 自定义前缀
python3 scripts/generate_beta_codes.py -n 50 -p "STEPWISE" -o codes.csv

# 调整随机长度（默认 8）
python3 scripts/generate_beta_codes.py -n 10 -l 12 -o codes.csv
```

### 邀请码格式

- **默认格式**: `MATH-XXXX-XXXX`
- **字符集**: 大写字母 + 数字（排除 0,O,1,I,L 避免混淆）
- **有效期**: 90 天
- **示例**: `MATH-68AT-9QMJ`, `MATH-CR8K-9EZZ`

## 🔍 验证邀请码

### 检查有效性

```bash
# 验证单个邀请码
python3 scripts/verify_beta_code.py MATH-68AT-9QMJ

# 输出示例：
# ✅ 有效: Valid (89 days remaining)
#    创建时间: 2026-01-09 22:17:29
#    过期时间: 2026-04-09 22:17:29
#    状态: active
```

### 标记为已使用

```bash
# 标记邀请码已被使用
python3 scripts/verify_beta_code.py MATH-68AT-9QMJ \
  --mark-used \
  --user "user@example.com"
```

### 指定数据文件

```bash
python3 scripts/verify_beta_code.py \
  --file beta_codes_backup.csv \
  --code MATH-68AT-9QMJ
```

## 📊 查看统计

```bash
# 基础统计
python3 scripts/beta_stats.py

# 输出示例：
# ============================================================
# 📊 Beta 邀请码统计
# ============================================================
#
# 📝 总数: 100
# ✅ 有效: 100 (100.0%)
# ❌ 无效: 0 (0.0%)
#
# 详细状态:
#   • Active (未使用): 100
#   • Used (已使用): 0
#   • Expired (已过期): 0
#
# 📈 使用率: 0.0%
# 📉 剩余可用: 100

# 显示用户列表
python3 scripts/beta_stats.py --show-users
```

## 📋 CSV 文件格式

生成的 `beta_codes.csv` 包含以下字段：

| 字段         | 说明     | 示例                |
| ------------ | -------- | ------------------- |
| `code`       | 邀请码   | MATH-68AT-9QMJ      |
| `created_at` | 创建时间 | 2026-01-09 22:17:29 |
| `expires_at` | 过期时间 | 2026-04-09 22:17:29 |
| `status`     | 状态     | active / used       |
| `used_by`    | 使用者   | user@example.com    |
| `used_at`    | 使用时间 | 2026-01-15 10:30:00 |
| `notes`      | 备注     | （可手动添加）      |

## 🔄 工作流程

### 1. 启动 Beta 前

```bash
# 生成邀请码
python3 scripts/generate_beta_codes.py -n 100 -o beta_codes.csv

# 查看统计
python3 scripts/beta_stats.py

# 备份邀请码库
cp beta_codes.csv beta_codes_backup.csv
```

### 2. 用户注册时

```bash
# 验证邀请码
python3 scripts/verify_beta_code.py MATH-XXXX-XXXX

# 如果有效，标记为已使用
python3 scripts/verify_beta_code.py MATH-XXXX-XXXX \
  --mark-used \
  --user "user@example.com"
```

### 3. 定期检查

```bash
# 查看使用情况
python3 scripts/beta_stats.py --show-users

# 检查即将过期的邀请码（手动查看 CSV）
# 可以用 Excel/Numbers 打开 beta_codes.csv 查看
```

## 🔗 后端集成

### FastAPI 路由示例

```python
from fastapi import APIRouter, HTTPException
import csv
from datetime import datetime, timezone

router = APIRouter()

def verify_beta_code(code: str) -> bool:
    """验证 beta 邀请码"""
    codes = {}
    with open('beta_codes.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes[row['code']] = row

    if code not in codes:
        return False

    code_data = codes[code]

    # 检查状态
    if code_data['status'] != 'active':
        return False

    # 检查过期
    expires_at = datetime.strptime(code_data['expires_at'], '%Y-%m-%d %H:%M:%S')
    expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        return False

    return True

@router.post("/api/verify-beta-code")
async def verify_code(code: str):
    """验证 beta 邀请码"""
    if verify_beta_code(code):
        return {"valid": True, "message": "Welcome to StepWise Beta!"}
    else:
        raise HTTPException(status_code=403, message="Invalid or expired code")
```

## 🔒 安全注意事项

1. **不要提交到 Git**
   - `beta_codes.csv` 已加入 `.gitignore`
   - 包含敏感邀请码，不应公开

2. **定期备份**

   ```bash
   cp beta_codes.csv backups/beta_codes_$(date +%Y%m%d).csv
   ```

3. **限制访问权限**

   ```bash
   chmod 600 beta_codes.csv
   ```

4. **监控使用情况**
   - 定期运行统计脚本
   - 检查异常使用模式
   - 防止邀请码滥用

## 📈 扩展功能

### 批量导入用户

如果需要批量标记邀请码为已使用：

```python
# batch_import.py
import csv

users = [
    ("MATH-68AT-9QMJ", "user1@example.com"),
    ("MATH-9F54-RQR9", "user2@example.com"),
    # ...
]

for code, user in users:
    # 调用 verify_beta_code.py 的逻辑
    pass
```

### 导出报告

```bash
# 导出为 Excel 友好格式
cat beta_codes.csv | column -t -s, > beta_report.txt
```

## 🆘 故障排查

### 问题：邀请码无效

```bash
# 1. 检查邀请码是否存在
grep "MATH-XXXX-XXXX" beta_codes.csv

# 2. 验证格式
python3 scripts/verify_beta_code.py MATH-XXXX-XXXX

# 3. 查看详细信息
python3 -c "import csv; [print(row) for row in csv.DictReader(open('beta_codes.csv')) if row['code'] == 'MATH-XXXX-XXXX']"
```

### 问题：CSV 文件损坏

```bash
# 恢复备份
cp beta_codes_backup.csv beta_codes.csv

# 验证文件完整性
wc -l beta_codes.csv
head -1 beta_codes.csv  # 检查表头
```

## 📞 支持

遇到问题？检查以下资源：

- **脚本帮助**: `python3 scripts/generate_beta_codes.py --help`
- **验证帮助**: `python3 scripts/verify_beta_code.py --help`
- **统计帮助**: `python3 scripts/beta_stats.py --help`
