# AmneziaVPN Route Release Generator

通过 GitHub Actions 自动把 `input/*.txt` 中的 IP、CIDR 网段或域名批量写入 AmneziaVPN JSON 模板，并创建 GitHub Release。

## 目录

```text
.
├── .github/
│   └── workflows/
│       └── create-release.yml
├── input/
│   ├── ip-ranges.txt
│   └── domains.txt
├── scripts/
│   └── build_routes.py
├── template/
│   └── routes.template.json
└── README.md
```

## 输入规则

`input/` 下所有 `.txt` 文件都会被读取：

```text
# 注释
1.1.8.0/24
1.2.4.0/24
example.com
www.example.com
```

支持：
- IPv4 地址
- IPv4 CIDR 网段
- 常规域名
- `#` 行尾注释
- 多个 TXT 文件

脚本会自动：
- 去除空行和注释
- 校验 IPv4/CIDR
- 校验域名格式
- 去重
- 保留模板原有项目
- 按 IP/域名排序
- 生成标准 JSON

## 创建 Release

### 方法 1：Actions 页面手动运行

进入：

`Actions` → `Create Release` → `Run workflow`

填写：

```text
release_tag: v2026.10.14
prerelease: false
```

Workflow 会生成：

```text
dist/amnezia-routes.json
```

并把它作为 Release Asset 上传。

### 方法 2：推送 Git Tag

```bash
git tag v2026.10.14
git push origin v2026.10.14
```

会自动创建对应 Release。

## 修改模板

直接修改：

```text
template/routes.template.json
```

例如：

```json
[
    {
        "hostname": "192.168.10.1",
        "ip": "",
        "ips": []
    }
]
```

模板中的原有项目不会被删除。

## 关于 AmneziaVPN

本项目只负责生成 JSON 数据，不负责修改 AmneziaVPN 客户端本身。

如果后续确认 AmneziaVPN 的实际导入格式存在更严格的字段、顺序或语义要求，可以只修改 `scripts/build_routes.py`，Workflow 无需改变。
