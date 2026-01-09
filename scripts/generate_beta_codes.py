#!/usr/bin/env python3
"""
Beta 邀请码生成器
为 StepWise Private Beta 生成唯一的邀请码

Usage:
    python3 scripts/generate_beta_codes.py -n 100 -o beta_codes.csv
"""

import argparse
import csv
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path


def generate_code(length: int = 8, prefix: str = "MATH") -> str:
    """
    生成一个随机邀请码

    Args:
        length: 随机部分的长度
        prefix: 邀请码前缀

    Returns:
        格式化的邀请码，如 "MATH-AB12CD34"
    """
    # 使用大写字母和数字，排除易混淆的字符（0,O,1,I,L）
    alphabet = string.ascii_uppercase.replace('O', '').replace('I', '').replace('L', '') + '23456789'
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))

    # 每 4 个字符插入一个连字符
    formatted = '-'.join([random_part[i:i+4] for i in range(0, len(random_part), 4)])

    return f"{prefix}-{formatted}"


def generate_batch(count: int, prefix: str = "MATH", length: int = 8) -> list[dict]:
    """
    批量生成邀请码

    Args:
        count: 生成数量
        prefix: 邀请码前缀
        length: 随机部分长度

    Returns:
        邀请码列表，每个包含 code, created_at, expires_at, status, used_by, used_at
    """
    codes = set()
    result = []

    # 生成唯一邀请码
    while len(codes) < count:
        code = generate_code(length=length, prefix=prefix)
        if code not in codes:
            codes.add(code)

    # 添加元数据
    from datetime import timezone
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=90)  # 90 天有效期

    for code in codes:
        result.append({
            'code': code,
            'created_at': now.strftime('%Y-%m-%d %H:%M:%S'),
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active',
            'used_by': '',
            'used_at': '',
            'notes': ''
        })

    return result


def save_to_csv(codes: list[dict], output_path: Path):
    """保存到 CSV 文件"""
    fieldnames = ['code', 'created_at', 'expires_at', 'status', 'used_by', 'used_at', 'notes']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(codes)

    print(f"✅ 成功生成 {len(codes)} 个邀请码")
    print(f"📁 保存到: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description='为 StepWise Private Beta 生成邀请码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成 100 个邀请码
  python3 scripts/generate_beta_codes.py -n 100 -o beta_codes.csv

  # 生成 50 个自定义前缀的邀请码
  python3 scripts/generate_beta_codes.py -n 50 -p "STEPWISE" -o codes.csv

  # 生成 10 个短邀请码（6 位随机）
  python3 scripts/generate_beta_codes.py -n 10 -l 6
        """
    )

    parser.add_argument(
        '-n', '--count',
        type=int,
        required=True,
        help='生成数量'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default='beta_codes.csv',
        help='输出文件路径（默认: beta_codes.csv）'
    )

    parser.add_argument(
        '-p', '--prefix',
        type=str,
        default='MATH',
        help='邀请码前缀（默认: MATH）'
    )

    parser.add_argument(
        '-l', '--length',
        type=int,
        default=8,
        help='随机部分长度（默认: 8）'
    )

    args = parser.parse_args()

    # 验证参数
    if args.count <= 0:
        parser.error("生成数量必须大于 0")

    if args.length < 4:
        parser.error("随机部分长度不能小于 4")

    print(f"🔐 生成 {args.count} 个 beta 邀请码...")
    print(f"📝 前缀: {args.prefix}")
    print(f"📏 随机长度: {args.length}")
    print()

    # 生成邀请码
    codes = generate_batch(
        count=args.count,
        prefix=args.prefix,
        length=args.length
    )

    # 保存
    save_to_csv(codes, args.output)

    # 显示示例
    print()
    print("📋 示例邀请码（前 5 个）:")
    for i, code in enumerate(codes[:5], 1):
        print(f"  {i}. {code['code']}")

    if len(codes) > 5:
        print(f"  ... 还有 {len(codes) - 5} 个")

    print()
    print("💡 提示:")
    print("  - 邀请码有效期: 90 天")
    print("  - 使用状态: active（未使用）")
    print("  - 文件格式: CSV（可用 Excel 打开）")


if __name__ == '__main__':
    main()
