#!/usr/bin/env python3
"""
Beta 邀请码统计脚本
显示邀请码使用情况统计

Usage:
    python3 scripts/beta_stats.py
    python3 scripts/beta_stats.py --file beta_codes.csv
"""

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load_codes_from_csv(csv_path: Path) -> list[dict]:
    """从 CSV 文件加载邀请码"""
    codes = []

    if not csv_path.exists():
        return codes

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            codes.append(row)

    return codes


def analyze_codes(codes: list[dict]) -> dict:
    """分析邀请码统计信息"""
    now = datetime.now(timezone.utc)

    stats = {
        'total': len(codes),
        'active': 0,
        'used': 0,
        'expired': 0,
        'valid': 0,
        'invalid': 0,
        'users': []
    }

    for code in codes:
        status = code['status']

        # 统计状态
        if status == 'active':
            stats['active'] += 1
        elif status == 'used':
            stats['used'] += 1
            if code['used_by']:
                stats['users'].append(code['used_by'])

        # 检查过期
        expires_at = datetime.strptime(code['expires_at'], '%Y-%m-%d %H:%M:%S')
        expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now > expires_at:
            stats['expired'] += 1
            stats['invalid'] += 1
        else:
            if status == 'active':
                stats['valid'] += 1
            else:
                stats['invalid'] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='查看 beta 邀请码统计信息'
    )

    parser.add_argument(
        '--file',
        type=Path,
        default='beta_codes.csv',
        help='CSV 文件路径（默认: beta_codes.csv）'
    )

    parser.add_argument(
        '--show-users',
        action='store_true',
        help='显示已使用邀请码的用户列表'
    )

    args = parser.parse_args()

    # 检查文件
    if not args.file.exists():
        print(f"❌ 文件不存在: {args.file}")
        return

    # 加载数据
    codes = load_codes_from_csv(args.file)
    stats = analyze_codes(codes)

    # 显示统计
    print("=" * 60)
    print("📊 Beta 邀请码统计")
    print("=" * 60)
    print()

    print(f"📝 总数: {stats['total']}")
    print(f"✅ 有效: {stats['valid']} ({stats['valid']/stats['total']*100:.1f}%)")
    print(f"❌ 无效: {stats['invalid']} ({stats['invalid']/stats['total']*100:.1f}%)")
    print()

    print("详细状态:")
    print(f"  • Active (未使用): {stats['active']}")
    print(f"  • Used (已使用): {stats['used']}")
    print(f"  • Expired (已过期): {stats['expired']}")
    print()

    # 使用率
    usage_rate = stats['used'] / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f"📈 使用率: {usage_rate:.1f}%")
    print(f"📉 剩余可用: {stats['valid']}")
    print()

    # 用户列表
    if args.show_users and stats['users']:
        print("👥 使用者列表:")
        user_counts = Counter(stats['users'])
        for i, (user, count) in enumerate(user_counts.most_common(), 1):
            print(f"  {i}. {user} ({count} 次)")
        print()

    # 进度条
    bar_length = 40
    used_bar = int(bar_length * stats['used'] / stats['total'])
    valid_bar = int(bar_length * stats['valid'] / stats['total'])
    expired_bar = bar_length - used_bar - valid_bar

    print("进度:")
    print(f"  [{'█' * used_bar}{'░' * valid_bar}{' ' * expired_bar}]")
    print(f"  █ 已使用 {stats['used']}  ░ 可用 {stats['valid']}  ␣ 过期 {stats['expired']}")
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
