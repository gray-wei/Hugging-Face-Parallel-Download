# Hugging Face 模型集合下载工具

这个工具用于自动下载 Hugging Face 上的模型集合，特别是针对 Facebook 的 SPARSH 系列模型和数据集。

## 功能特点

- 自动抓取集合页面，获取所有模型/数据集的 ID
- 使用 Hugging Face Hub API 下载模型和数据集
- 支持进度显示和错误处理
- 提供两个版本：单线程和多线程并行下载
- 支持断点续传和失败重试
- 可配置下载间隔，避免触发 API 限制
- 提供单独下载特定模型的脚本

## 安装依赖

运行以下命令安装必要的依赖：

```bash
pip install huggingface_hub requests beautifulsoup4 tqdm
```

## 使用方法

### 基本用法（单线程版本）

```bash
python download_sparsh_models.py
```

这将下载 Facebook SPARSH 集合中的所有模型到 `./downloaded_models` 目录。

### 高级选项（单线程版本）

```bash
python download_sparsh_models.py --collection_url [URL] --output_dir [DIR] --token [TOKEN] --delay [SECONDS]
```

参数说明：

- `--collection_url`：Hugging Face 集合的 URL，默认为 Facebook SPARSH 集合
- `--output_dir`：下载模型的保存目录，默认为 `./downloaded_models`
- `--token`：Hugging Face API 令牌，用于访问私有模型（可选）
- `--delay`：每次下载之间的延迟秒数，默认为 2 秒

### 并行下载版本

```bash
python download_sparsh_models_parallel.py
```

### 并行下载高级选项

```bash
python download_sparsh_models_parallel.py --collection_url [URL] --output_dir [DIR] --token [TOKEN] --max_workers [NUM] --resume --retry_failed
```

并行版本特有参数：

- `--max_workers`：最大并行下载线程数，默认为 3
- `--resume`：尝试恢复未完成的下载
- `--retry_failed`：重试之前失败的下载

### 下载特定模型

如果您只想下载特定的模型，可以使用 `download_specific_model.py` 脚本：

```bash
python download_specific_model.py --model_id [MODEL_ID] --output_dir [DIR] --token [TOKEN] --resume
```

参数说明：

- `--model_id`：要下载的模型ID，格式为"用户名/模型名"（必需）
- `--output_dir`：下载模型的保存目录，默认为 `./downloaded_models`
- `--token`：Hugging Face API 令牌，用于访问私有模型（可选）
- `--resume`：尝试恢复未完成的下载

示例：

```bash
python download_specific_model.py --model_id facebook/sparsh-tactile-bert
```

## 并行下载特性

并行版本提供以下额外功能：

1. **并行下载**：同时下载多个模型，大幅提高下载效率
2. **断点续传**：支持恢复中断的下载
3. **失败记录**：自动记录下载失败的模型
4. **重试机制**：支持重试之前失败的下载
5. **日志系统**：详细的日志记录，方便追踪下载状态

## 使用 Hugging Face 令牌

对于某些模型，您可能需要使用 Hugging Face 令牌来授权下载。您可以通过以下步骤获取令牌：

1. 登录 Hugging Face 网站
2. 点击右上角头像 -> Settings -> Access Tokens
3. 创建一个新的访问令牌
4. 使用 `--token` 参数提供这个令牌

```bash
python download_sparsh_models_parallel.py --token YOUR_TOKEN_HERE
```

## 注意事项

- 下载大型模型可能需要较长时间和大量存储空间
- 请确保您有足够的网络带宽和磁盘空间
- 对于非常大的模型（例如几十 GB），可能需要单独下载
- 过于频繁的下载请求可能会被 Hugging Face 限制，请适当设置并行数量
- 推荐为大型下载使用稳定的网络连接

## 示例用法

### 示例 1：基本下载

```bash
python download_sparsh_models_parallel.py
```

### 示例 2：指定输出目录并设置并行数

```bash
python download_sparsh_models_parallel.py --output_dir ./sparsh_models --max_workers 5
```

### 示例 3：使用令牌并启用断点续传

```bash
python download_sparsh_models_parallel.py --token YOUR_TOKEN --resume
```

### 示例 4：重试失败的下载

```bash
python download_sparsh_models_parallel.py --retry_failed
```

### 示例 5：下载单个特定模型

```bash
python download_specific_model.py --model_id facebook/sparsh-tactile-bert --resume
```

## 常见问题

1. **下载出错**：检查网络连接和磁盘空间，可以使用 `--retry_failed` 选项重试
2. **权限错误**：确保您提供了正确的访问令牌，并且有权限访问相应的模型
3. **文件不完整**：使用 `--resume` 选项恢复下载
4. **下载速度慢**：适当增加 `--max_workers` 的值，但不要设置太高以避免被限制
5. **内存使用过高**：减少 `--max_workers` 的值 