import requests

def quick_tts(api_key: str, text: str, prompt_audio_path: str = None):
    """
    快速语音合成
    
    Args:
        api_key: API 密钥
        text: 要合成的文本
        prompt_audio_path: 参考音频路径（可选）
    """
    url = "https://indextts.cn/tts"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {"text": text, "temperature": "0.7"}
    files = {}
    
    if prompt_audio_path:
        files["prompt_audio"] = open(prompt_audio_path, "rb")
    
    try:
        response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # 保存音频
            filename = f"tts_output.wav"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ 合成成功！文件保存为: {filename}")
            return filename
        else:
            print(f"❌ 合成失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None
    finally:
        if files:
            files["prompt_audio"].close()

# 使用示例
if __name__ == "__main__":
    # 最简单用法
    quick_tts(
        api_key="416cba8e-6fdd-4adb-b9b2-60f44ee2ae64",  # 替换为您的 API key
        text="你好，这是一个快速语音合成测试。"
    )