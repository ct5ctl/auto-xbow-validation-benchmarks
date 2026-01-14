#!/usr/bin/env python
"""
批量修改所有 benchmark 的端口映射
将端口按编号分配：001 -> 60001, 002 -> 60002, ...
"""

import os
import re
import sys

def extract_benchmark_number(benchmark_path):
    """从路径中提取 benchmark 编号，如 XBEN-001-24 -> 1"""
    match = re.search(r'XBEN-(\d+)-', benchmark_path)
    if match:
        return int(match.group(1))
    return None

def update_docker_compose_ports(file_path, benchmark_num):
    """更新 docker-compose.yml 文件中的端口映射"""
    target_port = 60000 + benchmark_num
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print("Error reading {path}: {err}".format(path=file_path, err=e))
        return False
    
    original_content = content
    
    # 匹配 "80:80" 格式的端口映射，可能前面有空格或引号
    # 匹配格式：- "80:80" 或 - "80:80" 或 - 80:80
    pattern = r'(\s+-\s+)"80:80"'
    replacement = r'\1"{port}:80"'.format(port=target_port)
    
    content = re.sub(pattern, replacement, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated {path} -> port {port}".format(path=file_path, port=target_port))
            return True
        except Exception as e:
            print("Error writing {path}: {err}".format(path=file_path, err=e))
            return False
    else:
        print("No ports found to update in {path}".format(path=file_path))
        return False

def main():
    base_dir = "benchmarks"
    if not os.path.isdir(base_dir):
        print("Error: benchmarks directory not found")
        sys.exit(1)
    
    updated_count = 0
    skipped_count = 0
    
    # 遍历所有 benchmark 目录
    for item in sorted(os.listdir(base_dir)):
        benchmark_path = os.path.join(base_dir, item)
        if not os.path.isdir(benchmark_path):
            continue
        
        benchmark_num = extract_benchmark_number(item)
        if benchmark_num is None:
            print("Skipping {item}: cannot extract number".format(item=item))
            skipped_count += 1
            continue
        
        docker_compose_path = os.path.join(benchmark_path, "docker-compose.yml")
        if not os.path.isfile(docker_compose_path):
            print("Skipping {item}: docker-compose.yml not found".format(item=item))
            skipped_count += 1
            continue
        
        if update_docker_compose_ports(docker_compose_path, benchmark_num):
            updated_count += 1
    
    print("\nSummary:")
    print("  Updated: {updated}".format(updated=updated_count))
    print("  Skipped: {skipped}".format(skipped=skipped_count))

if __name__ == "__main__":
    main()
