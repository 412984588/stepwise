#!/usr/bin/env python3
"""
Beta 邀请码验证脚本
验证指定邀请码的状态和有效性

Usage:
    python3 scripts/verify_beta_code.py MATH-AB12-CD34
    python3 scripts/verify_beta_code.py --file beta_codes.csv --code MATH-AB12-CD34
"""

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_codes_from_csv(csv_path: Path) -> dict:
    """从 CSV 文件加载邀请码"""
    codes = {}

    if not csv_path.exists():
        return codes

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes[row['code']] = row

    return codes


def verify_code(code: str, codes: dict) -> dict:
    """
    验证邀请码

    Returns:
        {
            'valid': bool,
            'reason': str,
            'details': dict
        }
    """
    # 检查是否存在
    if code not in codes:
        return {
            'valid': False,
            'reason': 'Code not found',
            'details': None
        }

    code_data = codes[code]

    # 检查状态
    if code_data['status'] != 'active':
        return {
            'valid': False,
            'reason': f"Code status is '{code_data['status']}'",
            'details': code_data
        }

    # 检查是否已使用
    if code_data['used_by']:
        return {
            'valid': False,
            'reason': f"Code already used by '{code_data['used_by']}' at {code_data['used_at']}",
            'details': code_data
        }

    # 检查有效期
    expires_at = datetime.strptime(code_data['expires_at'], '%Y-%m-%d %H:%M:%S')
    expires_at = expires_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if now > expires_at:
        return {
            'valid': False,
            'reason': f"Code expired at {code_data['expires_at']}",
            'details': code_data
        }

    # 验证通过
    days_left = (expires_at - now).days
    return {
        'valid': True,
        'reason': f"Valid ({days_left} days remaining)",
        'details': code_data
    }


def mark_as_used(csv_path: Path, code: str, used_by: str):
    """标记邀请码为已使用"""
    codes = load_codes_from_csv(csv_path)

    if code not in codes:
        print(f"❌ 邀请码不存在: {code}")
        return False

    # 更新状态
    codes[code]['status'] = 'used'
    codes[code]['used_by'] = used_by
    codes[code]['used_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # 写回文件
    fieldnames = ['code', 'created_at', 'expires_at', 'status', 'used_by', 'used_at', 'notes']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(codes.values())

    print(f"✅ 邀请码已标记为使用: {code}")
    print(f"   使用者: {used_by}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='验证 beta 邀请码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 验证单个邀请码
  python3 scripts/verify_beta_code.py MATH-AB12-CD34

  # 验证并标记为已使用
  python3 scripts/verify_beta_code.py MATH-AB12-CD34 --mark-used --user "user@example.com"

  # 指定 CSV 文件
  python3 scripts/verify_beta_code.py --file beta_codes.csv --code MATH-AB12-CD34
        """
    )

    parser.add_argument(
        'code',
        nargs='?',
        help='邀请码'
    )

    parser.add_argument(
        '--file',
        type=Path,
        default='beta_codes.csv',
        help='CSV 文件路径（默认: beta_codes.csv）'
    )

    parser.add_argument(
        '--code',
        dest='code_arg',
        help='邀请码（可选，优先于位置参数）'
    )

    parser.add_argument(
        '--mark-used',
        action='store_true',
        help='标记为已使用'
    )

    parser.add_argument(
        '--user',
        help='使用者标识（邮箱或用户名）'
    )

    args = parser.parse_args()

    # 确定邀请码
    code = args.code_arg or args.code
    if not code:
        parser.error("请提供邀请码")

    # 检查文件
    if not args.file.exists():
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)

    # 加载邀请码
    print(f"📁 加载邀请码库: {args.file}")
    codes = load_codes_from_csv(args.file)
    print(f"📊 总数: {len(codes)} 个邀请码")
    print()

    # 验证
    print(f"🔍 验证邀请码: {code}")
    result = verify_code(code, codes)

    # 显示结果
    if result['valid']:
        print(f"✅ 有效: {result['reason']}")
        if result['details']:
            print(f"   创建时间: {result['details']['created_at']}")
            print(f"   过期时间: {result['details']['expires_at']}")
            print(f"   状态: {result['details']['status']}")
    else:
        print(f"❌ 无效: {result['reason']}")
        if result['details']:
            print(f"   创建时间: {result['details']['created_at']}")
            print(f"   过期时间: {result['details']['expires_at']}")
            print(f"   状态: {result['details']['status']}")
            if result['details']['used_by']:
                print(f"   使用者: {result['details']['used_by']}")
                print(f"   使用时间: {result['details']['used_at']}")

    # 标记为已使用
    if args.mark_used:
        print()
        if not result['valid']:
            print("⚠️  邀请码无效，无法标记为使用")
            sys.exit(1)

        if not args.user:
            parser.error("--mark-used 需要提供 --user 参数")

        mark_as_used(args.file, code, args.user)

    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
