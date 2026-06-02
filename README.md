# PDFGet - 智能文献搜索与批量下载工具

![PyPI](https://img.shields.io/pypi/v/pdfget-refine) ![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue) ![License](https://img.shields.io/pypi/l/pdfget-refine)

> 注意：本仓库为 [gqy20/pdfget](https://github.com/gqy20/pdfget) 的 fork，基于上游 commit `e0f5da8a493ed88dad50b477f407214e3ca3d4f9`（记录时间：2026-04-01T16:17:46+08:00）。
> 原始作者：gqy；维护者/贡献者：jqming123。


PDFGet 是一个面向科研场景的命令行工具，支持 PubMed、Europe PMC 和 arXiv 的检索、统计与批量下载。

## 当前能力

- 支持 `-s` 按关键词搜索，或 `-m` 直接输入 CSV / TSV / 单个标识符 / 逗号分隔列表
- 支持混合标识符下载：PMCID、PMID、DOI、arXiv ID
- 支持数据源切换：`pubmed`、`europe_pmc`、`arxiv`、`both`、`all`
- 支持统计模式、下载模式，以及 `console` / `json` / `markdown` 输出
- 支持并发下载和本地缓存，适合批量处理

## 安装

### 环境要求

- Python 3.12 或更高版本

### 从 PyPI 安装

```bash
pip install pdfget
```

### 使用 uv

```bash
uv add pdfget
```

### 从源码安装

```bash
git clone <your-repo-url>
cd pdfget
pip install -e .

# 开发环境（推荐）
uv sync --dev
```

## 快速开始

## 临时 PMC OA 访问说明

注意：PMC 于 2026-04-13 调整了其云端分发结构，部分旧的 OA 文件已被移动到带有 `deprecated/` 前缀的目录中。
为了保持向后兼容，pdfget 会在对 PMC OA 遗留路径的访问中临时插入 `deprecated/` 前缀以检索这些文件。请注意，该临时兼容方法将在 2026 年 8 月失效（遗留目录将被移除），建议尽快更新自动化脚本以使用新的 S3 结构或参考 NCBI 的 eSearch→S3 管道检索方式。


### 搜索和统计

```bash
# 搜索并显示 PMCID 统计
pdfget -s "cancer immunotherapy" -l 100

# 搜索 PubMed 中可下载的文献
pdfget -s "machine learning AND pubmed pmc[sb]" -l 50

# 搜索 arXiv
pdfget -s "vision transformer" -S arxiv -l 20

# 联合搜索三个数据源
pdfget -s "large language model" -S all -l 30
```

### 下载

```bash
# 下载搜索结果
pdfget -s "cancer AND pubmed pmc[sb]" -l 20 -d

# 使用 AWS S3 访问 PMC OA（推荐在 PMC OA Web Service 变动时使用）
pdfget -s "cancer AND pubmed pmc[sb]" -l 20 -d -aws

# 下载 arXiv 论文
pdfget -s "diffusion model" -S arxiv -l 10 -d

# 直接下载单个标识符
pdfget -m "PMC5764346" -d
pdfget -m "10.1186/s12916-020-01690-4" -d
pdfget -m "2301.12345" -d

# 批量下载混合标识符
pdfget -m "PMC123456,38238491,10.1038/xxxx,2301.12345" -d -t 5
```

### CSV / TSV 批量输入

```bash
# 自动识别列名
pdfget -m identifiers.csv -d

# TSV 文件同样支持
pdfget -m identifiers.tsv -d

# 指定 CSV / TSV 列名
pdfget -m data.csv -c PMCID -d
```

## 常用参数

- `-s QUERY` 搜索文献
- `-m INPUT` CSV / TSV 文件、单个标识符或逗号分隔列表
- `-c COLUMN` CSV / TSV 列名，默认自动检测 `ID`、`PMCID`、`doi`、`pmid`、第一列
- `-d` 下载 PDF；不加时默认输出统计结果
- `-l NUM` 处理数量，默认 200
- `-t NUM` 并发线程数，默认 3
- `--delay SEC` 下载延迟，默认 1.0
- `-o DIR` 输出目录，默认 `pdfs`
- `-v` 详细输出
- `-S SOURCE` 数据源，支持 `pubmed`、`europe_pmc`、`arxiv`、`both`、`all`
- `-aws` 使用 AWS S3 访问 PMC OA（无需账号）
- `--format FORMAT` 输出格式，支持 `console`、`json`、`markdown`
- `-e EMAIL` NCBI API 邮箱
- `-k KEY` NCBI API 密钥

缓存目录默认 `~/.cache/pdfget`，可通过 `PDFGET_CACHE_DIR` 环境变量覆盖。

## 结构化输出

当使用 `--format json` 时，搜索与下载结果会输出为结构化 JSON，适合脚本和自动化流程使用。

- 搜索结果使用 `paper_record.v1`
- 下载结果使用 `download_result.v1`

示例：

```bash
pdfget -s "vision transformer" -S arxiv --format json > search.json
pdfget -s "vision transformer" -S arxiv -d --format json > download.json
```

## 适用场景

- 需要从 PubMed / Europe PMC 检索开放获取文献
- 已知 PMCID、PMID、DOI 或 arXiv ID，想批量下载 PDF
- 需要对搜索结果做自动化处理、统计或二次集成

## 文档

- [用户详细文档](docs/USER_GUIDE.md)
- [Schema Guide](docs/SCHEMA.md)
- [许可证](docs/LICENSE.md)

## 相关链接

- [更新日志](docs/CHANGELOG.md)
