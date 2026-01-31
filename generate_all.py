#!/usr/bin/env python3
"""
统一RSS生成器
运行所有RSS源的生成脚本
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


def find_source_files():
    """查找所有RSS源文件"""
    sources_dir = Path(__file__).parent / 'sources'
    if not sources_dir.exists():
        print(f"错误: sources目录不存在: {sources_dir}")
        return []
    
    source_files = list(sources_dir.glob('*.py'))
    # 排除__init__.py等特殊文件
    source_files = [f for f in source_files if not f.name.startswith('_')]
    return source_files


def run_source(source_file):
    """运行单个RSS源生成器"""
    print(f"\n{'='*60}")
    print(f"运行: {source_file.stem}")
    print('='*60)
    
    try:
        # 使用subprocess运行，保持独立环境
        result = subprocess.run(
            [sys.executable, str(source_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 输出标准输出
        if result.stdout:
            print(result.stdout, end='')
        
        # 输出标准错误
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        
        if result.returncode == 0:
            print(f"✓ {source_file.stem} 生成成功")
            return True
        else:
            print(f"✗ {source_file.stem} 生成失败 (退出码: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {source_file.stem} 超时")
        return False
    except Exception as e:
        print(f"✗ {source_file.stem} 执行出错: {e}")
        return False


def main():
    print("=" * 60)
    print("RSS 统一生成器")
    print("=" * 60)
    
    # 查找所有源文件
    source_files = find_source_files()
    
    if not source_files:
        print("警告: 未找到任何RSS源文件")
        return 1
    
    print(f"\n找到 {len(source_files)} 个RSS源:")
    for f in source_files:
        print(f"  - {f.stem}")
    
    # 运行所有源
    results = {}
    for source_file in source_files:
        success = run_source(source_file)
        results[source_file.stem] = success
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("生成结果汇总")
    print('='*60)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for name, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {success_count}/{total_count} 成功")
    
    # 列出生成的RSS文件
    output_dir = Path(__file__).parent / 'output'
    if output_dir.exists():
        rss_files = list(output_dir.glob('*.xml'))
        if rss_files:
            print(f"\n生成的RSS文件 ({len(rss_files)}):")
            for rss_file in sorted(rss_files):
                size = rss_file.stat().st_size
                print(f"  - {rss_file.name} ({size:,} bytes)")
    
    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
