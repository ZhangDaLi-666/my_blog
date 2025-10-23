# 上海兴交教育网新闻爬虫

该项目提供一个使用 Python 编写的爬虫脚本，用于抓取上海行健职业学院信息公开网（[http://www.shxj.edu.cn](http://www.shxj.edu.cn)）“新闻发布”栏目下的全部新闻，并将数据存入 MySQL 数据库。

## 功能概览

- 自动遍历新闻分页（含尾页检测）
- 抓取每篇新闻的标题与正文内容
- 使用 `requests` + `BeautifulSoup` 解析网页
- 将数据持久化到 MySQL 数据库（如已存在则更新）
- 提供数据库表结构 SQL、依赖清单以及配置样例
- 内置请求重试、错误处理与抓取延迟以避免高频访问

## 环境准备

1. **Python 版本**：建议使用 Python 3.10 及以上版本。
2. **创建虚拟环境（可选但推荐）**：

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **安装依赖**：

   ```bash
   pip install -r requirements.txt
   ```

## 数据库准备

1. 启动 MySQL 服务，并确保拥有创建数据库与表的权限。
2. 执行 `database_schema.sql`，创建数据库及表结构：

   ```bash
   mysql -u <username> -p < database_schema.sql
   ```

   默认会创建名为 `shxj_news` 的数据库以及 `news_articles` 表，表结构中包含 `title`、`url`、`content` 等字段，字符集使用 `utf8mb4` 以支持中文内容。

   如果更偏向自动化方式，可直接运行辅助脚本完成相同操作：

   ```bash
   python setup_database.py
   ```

## 配置说明

- 将 `.env.example` 复制为 `.env` 并根据实际环境修改数据库连接信息：

  ```bash
  cp .env.example .env
  ```

- `.env` 中可配置的字段：

  | 环境变量       | 说明                | 默认值        |
  | -------------- | ------------------- | ------------- |
  | `DB_HOST`      | MySQL 主机地址      | `localhost`   |
  | `DB_PORT`      | MySQL 端口          | `3306`        |
  | `DB_USER`      | 数据库用户名        | `root`        |
  | `DB_PASSWORD`  | 数据库密码          | 空字符串      |
  | `DB_NAME`      | 数据库名称          | `shxj_news`   |
  | `REQUEST_DELAY`| 每次请求之间的延迟（秒）| `1.0`      |

  爬虫默认会在每次抓取详情页和翻页之间等待至少 0.5 秒，可通过 `REQUEST_DELAY` 调整。

## 运行爬虫

确保已经配置好数据库并安装依赖后，运行以下命令启动爬虫：

```bash
python scraper.py
```

脚本将按页抓取所有新闻，保存到 `news_articles` 表中。若某篇文章已存在，则会更新其标题与正文内容。

## 代码结构

```
.
├── scraper.py             # 主爬虫脚本
├── config.py              # 全局配置（数据库、URL、延迟等）
├── setup_database.py      # 数据库初始化辅助脚本
├── requirements.txt       # Python 依赖列表
├── database_schema.sql    # MySQL 数据库与表结构（SQL 方式）
├── README.md              # 使用说明文档
└── .env.example           # 环境变量配置样例
```

## 注意事项

- 爬虫仅用于公开信息采集，请遵守目标网站的`robots.txt`及相关法律法规。
- 若目标网站结构发生变化，需要适当调整解析逻辑。
- 建议在低流量时段运行，并适当增大抓取间隔，以减轻目标服务器压力。
