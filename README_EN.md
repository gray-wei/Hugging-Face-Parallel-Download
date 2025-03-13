# transfer Chinese to English

# Hugging Face Model Collection Download Tool

This tool is used to automatically download model collections on Hugging Face, as an example of the Facebook SPARSH collection, users can modify the collection URL to download models from other collections.

## Features

- Automatically scrape the collection page to get all model/dataset IDs
- Use Hugging Face Hub API to download models and datasets
- Support progress display and error handling
- Provide two versions: single-threaded and multi-threaded parallel downloads
- Support resume and retry failed downloads
- Configurable download interval to avoid triggering API limits
- Provide a script to download specific models separately

## Install dependencies

Run the following command to install the necessary dependencies:

```bash
pip install huggingface_hub requests beautifulsoup4 tqdm
```

## Usage

### Basic usage (single-threaded version)

```bash
python download_sparsh_models.py
```

This will download all models from the Facebook SPARSH collection to the `./downloaded_models` directory.

### Advanced options (single-threaded version)

```bash
python download_sparsh_models.py --collection_url [URL] --output_dir [DIR] --token [TOKEN] --delay [SECONDS]
```

Parameters:

- `--collection_url`：Hugging Face collection URL, default is Facebook SPARSH collection
- `--output_dir`：Download model save directory, default is `./downloaded_models`
- `--token`：Hugging Face API token, for accessing private models (optional)
- `--delay`：Delay seconds between each download, default is 2 seconds

### Parallel download version

```bash
python download_sparsh_models_parallel.py
```

### Parallel download advanced options

```bash
python download_sparsh_models_parallel.py --collection_url [URL] --output_dir [DIR] --token [TOKEN] --max_workers [NUM] --resume --retry_failed
```

Parallel version specific parameters:

- `--max_workers`：Maximum number of parallel download threads, default is 3
- `--resume`：Try to resume unfinished downloads
- `--retry_failed`：Retry failed downloads

### Download specific models

If you only want to download specific models, you can use the `download_specific_model.py` script:

```bash
python download_specific_model.py --model_id [MODEL_ID] --output_dir [DIR] --token [TOKEN] --resume
```

Parameters:

- `--model_id`：The ID of the model to download, format is "username/modelname" (required)
- `--output_dir`：Download model save directory, default is `./downloaded_models`
- `--token`：Hugging Face API token, for accessing private models (optional)
- `--resume`：Try to resume unfinished downloads

Example:

```bash
python download_specific_model.py --model_id facebook/sparsh-tactile-bert
```

## Parallel download features

The parallel version provides the following additional features:

1. **Parallel download**：Download multiple models simultaneously,大幅提高下载效率
2. **Resume**：Support resuming interrupted downloads
3. **Failed record**：Automatically record failed downloads
4. **Retry mechanism**：Support retrying failed downloads
5. **Logging system**：Detailed logging for tracking download status

## Use Hugging Face token

For some models, you may need to use a Hugging Face token to authorize the download. You can get a token by following these steps:

1. Login to Hugging Face website
2. Click the avatar -> Settings -> Access Tokens
3. Create a new access token
4. Use the `--token` parameter to provide this token

```bash
python download_sparsh_models_parallel.py --token YOUR_TOKEN_HERE
```

## Notes

- Downloading large models may require a longer time and a lot of storage space
- Please ensure you have enough network bandwidth and disk space
- For very large models (e.g., several tens of GB), it may be necessary to download them separately
- Frequent download requests may be limited by Hugging Face, please set the parallel number appropriately
- It is recommended to use a stable network connection for large downloads

## Example usage

### Example 1: Basic download

```bash
python download_sparsh_models_parallel.py
```

### Example 2: Specify output directory and set parallel number

```bash
python download_sparsh_models_parallel.py --output_dir ./sparsh_models --max_workers 5
```

### Example 3: Use token and enable resume

```bash
python download_sparsh_models_parallel.py --token YOUR_TOKEN --resume
```

### Example 4: Retry failed downloads

```bash
python download_sparsh_models_parallel.py --retry_failed
```

### Example 5: Download a single specific model

```bash
python download_specific_model.py --model_id facebook/sparsh-tactile-bert --resume
```

## Common problems

1. **Download error**：Check network connection and disk space, you can use the `--retry_failed` option to retry
2. **Permission error**：Ensure you provided the correct access token and have access to the corresponding model
3. **File incomplete**：Use the `--resume` option to resume download
4. **Download speed slow**：Increase the value of `--max_workers` appropriately, but do not set it too high to avoid being limited
5. **Memory usage too high**：Reduce the value of `--max_workers`