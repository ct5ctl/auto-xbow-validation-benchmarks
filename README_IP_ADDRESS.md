# Benchmark IP 地址说明

## 获取 Benchmark 容器的 IP 地址

### 方法1: 使用脚本（推荐）

```bash
python get_benchmark_ip.py XBEN-006-24
```

### 方法2: 使用 Docker 命令

#### 查看所有运行中的容器及其IP：
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### 获取特定容器的IP地址：

**步骤1: 找到容器名称**
```bash
cd benchmarks/XBEN-006-24
docker compose ps
```

**步骤2: 获取容器IP**
```bash
# 方法A: 使用容器名称
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name>

# 方法B: 使用 docker compose
cd benchmarks/XBEN-006-24
docker compose exec app hostname -I
```

### 方法3: 查看所有网络信息

```bash
docker network ls
docker network inspect <network_name>
```

## IP 地址说明

### 默认情况
- Docker Compose 会为每个 benchmark 创建一个独立的网络
- 容器会获得一个私有 IP 地址（通常是 `172.x.x.x` 或 `192.168.x.x`）
- 这个 IP 只在 Docker 网络内部可见

### 访问方式

**从宿主机访问：**
- 使用映射的端口：`http://localhost:60006`（推荐）
- 使用容器IP：`http://<container_ip>:80`（需要先获取IP）

**从其他容器访问：**
- 使用服务名称：`http://app:80` 或 `http://web:80`
- 使用容器IP：`http://<container_ip>:80`

### 示例

假设 XBEN-006-24 的容器IP是 `172.18.0.2`：

```bash
# 从宿主机访问
curl http://localhost:60006
curl http://172.18.0.2:80

# 从其他容器访问（在docker-compose.yml中定义的服务）
curl http://app:80
```

## 注意事项

1. **容器IP是动态的**：每次重启容器，IP可能会变化
2. **推荐使用端口映射**：使用 `localhost:60006` 更稳定可靠
3. **服务名称**：在 docker-compose.yml 中定义的服务名可以在容器间直接使用
