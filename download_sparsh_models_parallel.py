#!/usr/bin/env python3
# 脚本用于并行下载Hugging Face上Facebook的SPARSH集合中的所有模型

import os
import requests
from bs4 import BeautifulSoup
import json
from huggingface_hub import hf_hub_download, snapshot_download
import re
import time
import argparse
from tqdm import tqdm
import concurrent.futures
import logging
from urllib.parse import urlparse, parse_qs

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_collection_models(collection_url):
    """获取集合中的所有模型/数据集信息"""
    logger.info(f"正在获取集合信息: {collection_url}")
    
    # 检查URL是否有效
    parsed_url = urlparse(collection_url)
    if not parsed_url.netloc or not parsed_url.path:
        raise ValueError("无效的集合URL")
    
    # 确保使用正确的用户代理以避免被拒绝
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(collection_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"无法访问集合页面，状态码: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 寻找包含模型信息的脚本标签
    scripts = soup.find_all('script')
    collection_data = None
    
    for script in scripts:
        if script.string and 'window.initialData=' in script.string:
            data_str = script.string.split('window.initialData=')[1].split(';</script>')[0]
            try:
                data = json.loads(data_str)
                if 'collection' in data and 'models' in data['collection']:
                    collection_data = data['collection']
                    break
            except json.JSONDecodeError:
                continue
    
    if not collection_data:
        # 尝试另一种方法：抓取模型卡片
        models = []
        model_cards = soup.select('article a[href^="/"]') or soup.select('a[href^="/"]')
        for card in model_cards:
            href = card.get('href', '')
            if href.startswith('/') and href.count('/') >= 1 and not href.startswith('/?'):
                model_id = href.lstrip('/')
                if model_id and '/' in model_id:  # 确保格式是 username/modelname
                    if not any(keyword in href for keyword in ['/discussions', '/settings', '/community']):
                        models.append(model_id)
        return list(set(models))  # 去重
    
    models = []
    for model in collection_data.get('models', []):
        if 'id' in model:
            models.append(model['id'])
    
    return models

def download_model(model_id, output_dir, use_auth_token=None, resume_download=True):
    """下载指定模型的所有文件"""
    try:
        output_path = os.path.join(output_dir, model_id.replace('/', '--'))
        os.makedirs(output_path, exist_ok=True)
        
        logger.info(f"开始下载模型: {model_id}")
        
        # 确定仓库类型
        repo_type = "dataset" if model_id.startswith("datasets/") else None
        
        # 如果是数据集类型，需要修正model_id格式
        if repo_type == "dataset":
            # 从datasets/facebook/name格式转换为facebook/name格式
            parts = model_id.split('/')
            if len(parts) >= 3:
                actual_model_id = f"{parts[1]}/{'/'.join(parts[2:])}"
            else:
                actual_model_id = model_id
        else:
            actual_model_id = model_id
        
        # 使用snapshot_download下载整个仓库
        snapshot_download(
            repo_id=actual_model_id,
            local_dir=output_path,
            token=use_auth_token,
            resume_download=resume_download,
            repo_type=repo_type,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"] if "--to--" in output_path else None
        )
        
        logger.info(f"模型 {model_id} 已下载成功到 {output_path}")
        return True, model_id
    except Exception as e:
        logger.error(f"下载模型 {model_id} 时出错: {str(e)}")
        return False, model_id

def download_worker(args):
    """并行下载的工作函数"""
    model_id, output_dir, token, resume = args
    return download_model(model_id, output_dir, token, resume)

def main():
    parser = argparse.ArgumentParser(description='下载Hugging Face集合中的所有模型')
    parser.add_argument('--collection_url', type=str, 
                        default='https://huggingface.co/collections/facebook/sparsh-67167ce57566196a4526c328',
                        help='Hugging Face集合URL')
    parser.add_argument('--output_dir', type=str, default='./downloaded_models',
                        help='下载模型的输出目录')
    parser.add_argument('--token', type=str, default=None,
                        help='Hugging Face API令牌，用于访问私有模型')
    parser.add_argument('--max_workers', type=int, default=3,
                        help='最大并行下载数量，默认为3')
    parser.add_argument('--resume', action='store_true',
                        help='尝试恢复未完成的下载')
    parser.add_argument('--retry_failed', action='store_true',
                        help='重试之前失败的下载')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 失败记录文件路径
    failed_log = os.path.join(args.output_dir, 'failed_downloads.txt')
    success_log = os.path.join(args.output_dir, 'successful_downloads.txt')
    
    # 加载之前保存的失败记录（如果启用了重试）
    failed_models = set()
    successful_models = set()
    
    if os.path.exists(success_log):
        with open(success_log, 'r') as f:
            successful_models = set(line.strip() for line in f)
    
    if args.retry_failed and os.path.exists(failed_log):
        with open(failed_log, 'r') as f:
            failed_models = set(line.strip() for line in f)
        logger.info(f"加载了 {len(failed_models)} 个失败的模型，将重试下载")
    
    # 获取集合中的模型
    model_ids = get_collection_models(args.collection_url)
    logger.info(f"在集合中找到了 {len(model_ids)} 个模型/数据集")
    
    # 过滤掉已成功下载的模型
    if successful_models:
        filtered_model_ids = [m for m in model_ids if m not in successful_models]
        logger.info(f"过滤掉 {len(model_ids) - len(filtered_model_ids)} 个已成功下载的模型")
        model_ids = filtered_model_ids
    
    # 如果启用重试，将失败模型添加到下载列表
    if args.retry_failed and failed_models:
        for failed_model in failed_models:
            if failed_model not in model_ids:
                model_ids.append(failed_model)
    
    if not model_ids:
        logger.info("没有需要下载的模型")
        return
    
    # 设置并行下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        download_args = [(model_id, args.output_dir, args.token, args.resume) for model_id in model_ids]
        results = list(tqdm(executor.map(download_worker, download_args), total=len(model_ids), desc="下载进度"))
    
    # 统计结果
    success_count = sum(1 for success, _ in results if success)
    failed_models = [model_id for success, model_id in results if not success]
    
    # 保存失败的下载记录
    if failed_models:
        with open(failed_log, 'w') as f:
            for model_id in failed_models:
                f.write(f"{model_id}\n")
    
    # 保存成功的下载记录
    with open(success_log, 'a') as f:
        for success, model_id in results:
            if success:
                f.write(f"{model_id}\n")
    
    logger.info(f"下载完成。成功: {success_count}/{len(model_ids)}, 失败: {len(failed_models)}")
    if failed_models:
        logger.info(f"失败的模型已记录到 {failed_log}")

if __name__ == "__main__":
    main() 