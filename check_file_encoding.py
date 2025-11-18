#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查文件编码的脚本
"""
import os
import chardet

def detect_encoding(file_path):
    """检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        return None, str(e)

def main():
    """主函数"""
    important_files = [
        'README.md',
        'app.py',
        'stats_core.py',
        'ollama_client.py',
        'requirements.txt'
    ]
    
    print("=" * 50)
    print("检查文件编码")
    print("=" * 50)
    print()
    
    for file in important_files:
        if os.path.exists(file):
            encoding, confidence = detect_encoding(file)
            status = "✓" if encoding and 'utf' in encoding.lower() else "✗"
            print(f"{status} {file:30s} - {encoding or 'Unknown':15s} (置信度: {confidence})")
        else:
            print(f"✗ {file:30s} - 文件不存在")
    
    print()
    print("=" * 50)
    print("建议:")
    print("- 如果编码不是 UTF-8，需要转换文件编码")
    print("- 在编辑器中打开文件，另存为 UTF-8 编码")
    print("=" * 50)

if __name__ == '__main__':
    main()

