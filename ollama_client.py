"""
Ollama 客户端封装
用于与本地或远程 Ollama 服务通信
"""
import requests
import json
import time
import os

# 从环境变量或 Streamlit Secrets 读取 Ollama API 地址
def get_ollama_url():
    """
    获取 Ollama API 地址
    优先级：Streamlit Secrets > 环境变量 > 默认本地地址
    """
    try:
        import streamlit as st
        # 尝试从 Streamlit Secrets 读取
        if hasattr(st, 'secrets') and 'ollama' in st.secrets:
            return st.secrets.ollama.get('api_url', 'http://localhost:11434')
    except:
        pass
    
    # 从环境变量读取
    return os.getenv('OLLAMA_API_URL', 'http://localhost:11434')

# 全局变量存储 API 地址
OLLAMA_API_URL = get_ollama_url()

def ask_model(prompt: str, system_prompt: str = "", max_retries: int = 2, timeout: int = 180) -> str:
    """
    向 Ollama 模型发送请求并获取回复（带重试机制）
    
    参数:
        prompt: 用户输入的问题/提示
        system_prompt: 系统提示词（可选）
        max_retries: 最大重试次数（默认2次）
        timeout: 请求超时时间（秒，默认180秒）
    
    返回:
        str: 模型的回复文本
    """
    # 默认系统提示词
    if not system_prompt:
        system_prompt = (
            "你是一个统计学与数据分析辅导助手，只能回答与统计分析、数据处理、可视化、"
            "出版级制图相关的问题。对于统计以外的医学、生物学、社会、政治等问题，"
            "一律回答：'抱歉，AI助手仅支持统计学分析与出版级图形生成相关的问题。' "
            "回答尽量简洁、使用中文。"
        )
    
    # Ollama API 端点
    url = f"{OLLAMA_API_URL}/api/chat"
    
    # 构建消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # 请求载荷
    payload = {
        "model": "tinyllama",  # 使用 tinyllama 模型（适合 2GB 内存服务器）
        "messages": messages,
        "stream": False  # 非流式响应
    }
    
    # 重试机制
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            # 发送 POST 请求
            response = requests.post(
                url,
                json=payload,
                timeout=timeout
            )
            
            # 检查 HTTP 状态码
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取回复内容
            if 'message' in result and 'content' in result['message']:
                content = result['message']['content'].strip()
                if content:
                    return content
                else:
                    return "抱歉，AI 返回了空回复，请重试。"
            else:
                return "抱歉，未能获取有效回复，请重试。"
        
        except requests.exceptions.ConnectionError as e:
            last_error = ConnectionError(
                f"无法连接到 Ollama 服务（{OLLAMA_API_URL}）。请确保：\n"
                "1. Ollama 已安装并正在运行\n"
                f"2. 服务地址为 {OLLAMA_API_URL}\n"
                "3. 模型 tinyllama 已下载（运行：ollama pull tinyllama）\n"
                "提示：在 Streamlit Cloud 部署时，需要配置远程 Ollama 服务地址"
            )
            if attempt < max_retries:
                time.sleep(1)  # 等待1秒后重试
                continue
            else:
                raise last_error
        
        except requests.exceptions.Timeout as e:
            last_error = TimeoutError(f"请求超时（{timeout}秒），请稍后重试。")
            if attempt < max_retries:
                time.sleep(2)  # 等待2秒后重试
                continue
            else:
                raise last_error
        
        except requests.exceptions.HTTPError as e:
            last_error = Exception(f"HTTP 错误：{e.response.status_code} - {e.response.text}")
            if attempt < max_retries:
                time.sleep(1)
                continue
            else:
                raise last_error
        
        except json.JSONDecodeError as e:
            last_error = ValueError("响应格式错误，无法解析 JSON。")
            if attempt < max_retries:
                time.sleep(1)
                continue
            else:
                raise last_error
        
        except Exception as e:
            last_error = Exception(f"未知错误：{str(e)}")
            if attempt < max_retries:
                time.sleep(1)
                continue
            else:
                raise last_error
    
    # 如果所有重试都失败
    raise last_error if last_error else Exception("请求失败，请重试。")


def test_connection() -> bool:
    """
    测试 Ollama 连接是否正常
    
    返回:
        bool: 连接是否成功
    """
    try:
        response = ask_model("你好", "你是一个测试助手，请回复'连接成功'。")
        return "连接成功" in response or len(response) > 0
    except:
        return False

