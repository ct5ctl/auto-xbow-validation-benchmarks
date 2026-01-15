#!/usr/bin/env python
"""
获取 benchmark 容器的 IP 地址
Usage: python get_benchmark_ip.py XBEN-006-24
"""

import subprocess
import sys
import os
import re

def get_container_name(benchmark_id):
    """根据 benchmark ID 生成容器名称"""
    # Docker Compose 的容器命名格式通常是: <project>_<service>_<number>
    # 项目名通常是目录名（小写，替换-为_）
    benchmark_lower = benchmark_id.lower().replace('-', '_')
    return benchmark_lower

def get_container_ip_by_name(benchmark_id):
    """通过容器名称查找IP地址"""
    benchmark_lower = benchmark_id.lower()
    
    # 尝试查找所有相关的容器
    try:
        # 获取所有运行中的容器
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = result.stdout.strip().split('\n')
        
        # 查找匹配的容器
        matching_containers = [c for c in containers if benchmark_lower in c.lower()]
        
        if not matching_containers:
            return None, "No running containers found for {bid}".format(bid=benchmark_id)
        
        # 获取第一个匹配容器的IP
        container_name = matching_containers[0]
        ip_result = subprocess.run(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name],
            capture_output=True,
            text=True,
            check=True
        )
        ip = ip_result.stdout.strip()
        
        if ip:
            return ip, container_name
        else:
            return None, "Container {name} has no IP address".format(name=container_name)
            
    except subprocess.CalledProcessError as e:
        return None, "Error: {err}".format(err=e.stderr)
    except FileNotFoundError:
        return None, "Error: docker command not found"

def get_container_ip_by_compose(benchmark_id):
    """通过 docker compose 获取容器IP"""
    benchmark_path = os.path.join("benchmarks", benchmark_id)
    if not os.path.isdir(benchmark_path):
        return None, "Benchmark directory not found"
    
    os.chdir(benchmark_path)
    try:
        # 获取服务名称
        result = subprocess.run(
            ["docker", "compose", "ps", "-q"],
            capture_output=True,
            text=True,
            check=True
        )
        container_ids = result.stdout.strip().split('\n')
        
        if not container_ids or not container_ids[0]:
            return None, "No running containers"
        
        # 获取第一个容器的IP
        container_id = container_ids[0]
        ip_result = subprocess.run(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_id],
            capture_output=True,
            text=True,
            check=True
        )
        ip = ip_result.stdout.strip()
        
        if ip:
            return ip, container_id
        else:
            return None, "Container has no IP address"
            
    except subprocess.CalledProcessError as e:
        return None, "Error: {err}".format(err=e.stderr)
    finally:
        os.chdir("../..")

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_benchmark_ip.py <BENCHMARK_ID>")
        print("Example: python get_benchmark_ip.py XBEN-006-24")
        sys.exit(1)
    
    benchmark_id = sys.argv[1]
    
    print("Looking for IP address of {bid}...".format(bid=benchmark_id))
    print("-" * 50)
    
    # 方法1: 通过 docker compose
    ip, info = get_container_ip_by_compose(benchmark_id)
    if ip:
        print("IP Address: {ip}".format(ip=ip))
        print("Container: {info}".format(info=info))
        print("\nAccess URL: http://{ip}:80".format(ip=ip))
        print("Mapped Port: http://localhost:600{num:02d}".format(num=int(benchmark_id.split('-')[1])))
        return
    
    # 方法2: 通过容器名称
    ip, info = get_container_ip_by_name(benchmark_id)
    if ip:
        print("IP Address: {ip}".format(ip=ip))
        print("Container: {info}".format(info=info))
        print("\nAccess URL: http://{ip}:80".format(ip=ip))
        return
    
    print("Could not find IP address: {info}".format(info=info))
    print("\nTips:")
    print("1. Make sure the benchmark is running: make run BENCHMARK={bid}".format(bid=benchmark_id))
    print("2. Check running containers: docker ps")
    print("3. Get all container IPs: docker inspect <container_name> | grep IPAddress")

if __name__ == "__main__":
    main()
