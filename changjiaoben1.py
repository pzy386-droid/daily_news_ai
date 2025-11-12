import requests
import os
from typing import Optional

class IndexTTS:
    def __init__(self, api_key: str, base_url: str = "https://indextts.cn"):
        """
        初始化 IndexTTS 客户端
        
        Args:
            api_key: 您的 API 密钥
            base_url: API 基础地址
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def synthesize(
        self,
        text: str,
        prompt_audio_path: Optional[str] = None,
        temperature: float = 0.7,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            prompt_audio_path: 参考音频文件路径（可选）
            temperature: 温度参数，控制随机性（0.0-1.0）
            output_path: 输出音频文件路径（可选，默认自动生成）
            
        Returns:
            音频文件路径，失败返回 None
        """
        # 构建请求数据
        data = {
            "text": text,
            "temperature": str(temperature)
        }
        
        files = {}
        if prompt_audio_path and os.path.exists(prompt_audio_path):
            files["prompt_audio"] = (
                os.path.basename(prompt_audio_path),
                open(prompt_audio_path, "rb"),
                self._get_mime_type(prompt_audio_path)
            )
        
        try:
            print(f"🚀 开始合成语音...")
            print(f"📝 文本: {text}")
            print(f"🎵 参考音频: {prompt_audio_path or '无'}")
            print(f"🌡️  温度: {temperature}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/tts",
                data=data,
                files=files if files else None,
                headers=self.headers,
                timeout=60
            )
            
            # 处理响应
            if response.status_code == 200:
                return self._handle_success_response(response, text, output_path)
            else:
                self._handle_error_response(response)
                return None
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
        finally:
            # 确保文件被关闭
            if files and "prompt_audio" in files:
                files["prompt_audio"][1].close()
    
    def _handle_success_response(self, response: requests.Response, text: str, output_path: str) -> str:
        """处理成功响应"""
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            # JSON 响应
            result = response.json()
            return self._process_json_response(result, text, output_path)
        else:
            # 直接返回音频文件
            return self._save_audio_file(response.content, text, output_path)
    
    def _process_json_response(self, result: dict, text: str, output_path: str) -> Optional[str]:
        """处理 JSON 响应"""
        # 根据实际 API 响应结构调整
        if 'audio_data' in result or 'audioData' in result:
            import base64
            audio_data = result.get('audio_data') or result.get('audioData')
            audio_bytes = base64.b64decode(audio_data)
            return self._save_audio_file(audio_bytes, text, output_path)
        elif 'audio_url' in result or 'audioUrl' in result:
            audio_url = result.get('audio_url') or result.get('audioUrl')
            return self._download_audio(audio_url, text, output_path)
        else:
            print("⚠️  响应格式未知，尝试直接保存...")
            return self._save_audio_file(response.content, text, output_path)
    
    def _save_audio_file(self, audio_content: bytes, text: str, output_path: str) -> str:
        """保存音频文件"""
        if not output_path:
            output_path = self._generate_output_filename(text)
        
        with open(output_path, 'wb') as f:
            f.write(audio_content)
        
        file_size = len(audio_content) / 1024  # KB
        print(f"✅ 音频合成成功！")
        print(f"💾 文件保存至: {output_path}")
        print(f"📊 文件大小: {file_size:.2f} KB")
        
        return output_path
    
    def _download_audio(self, audio_url: str, text: str, output_path: str) -> Optional[str]:
        """下载音频文件"""
        try:
            response = requests.get(audio_url, timeout=30)
            if response.status_code == 200:
                return self._save_audio_file(response.content, text, output_path)
            else:
                print(f"❌ 下载音频失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 下载音频失败: {e}")
            return None
    
    def _generate_output_filename(self, text: str) -> str:
        """生成输出文件名"""
        import re
        from datetime import datetime
        
        # 清理文本作为文件名
        clean_text = re.sub(r'[^\w\u4e00-\u9fff]', '_', text[:15])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"tts_{timestamp}_{clean_text}.wav"
    
    def _get_mime_type(self, file_path: str) -> str:
        """根据文件扩展名获取 MIME 类型"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _handle_error_response(self, response: requests.Response):
        """处理错误响应"""
        print(f"❌ 请求失败，状态码: {response.status_code}")
        try:
            error_data = response.json()
            print(f"错误信息: {error_data}")
        except:
            print(f"错误详情: {response.text}")

# 使用示例
def main():
    # 替换为您的实际 API 密钥
    API_KEY = "416cba8e-6fdd-4adb-b9b2-60f44ee2ae64"  # 请替换为您的真实 API key
    
    # 创建 TTS 客户端
    tts = IndexTTS(api_key=API_KEY, base_url="https://indextts.cn")
    
    # 示例1: 基础文本合成（无参考音频）
    print("=" * 50)
    result1 = tts.synthesize(
        text="你好，欢迎使用洛曦AI语音合成服务。这是一个测试语音。",
        temperature=0.7
    )
    
    # 示例2: 带参考音频的合成
    print("=" * 50)
    result2 = tts.synthesize(
        text="这段语音将参考提供的音频风格进行合成。",
        prompt_audio_path="./reference.wav",  # 替换为您的参考音频路径
        temperature=0.5,
        output_path="./custom_output.wav"  # 自定义输出路径
    )
    
    # 示例3: 长文本合成
    print("=" * 50)
    result3 = tts.synthesize(
        text="这是一个较长的文本示例，用于测试语音合成服务对长文本的处理能力。我们可以看到系统如何分段处理并生成连贯的语音输出。",
        temperature=0.8
    )

if __name__ == "__main__":
    main()