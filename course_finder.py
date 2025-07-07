import requests
import json

def make_get_request():
    """
    发送GET请求到中南大学教务系统
    """
    # 请求URL
    url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_jg0101.jsp"
    
    # 请求参数
    params = {
        'xnxq01id': '2024-2025-2',
        'init': '1',
        'isview': '1'
    }
    
    # 请求头
    headers = {
        'Host': 'csujwc.its.csu.edu.cn',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&xx04id=&isview=1&xnxq01id=2024-2025-2',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '_ga=GA1.1.2104536743.1742025470; _ga_PR7953H3X6=GS2.1.s1748770182$o51$g0$t1748770182$j60$l0$h0; JSESSIONID=A4C5E4CC52D43EFAA4A73B04E343FF57; SF_cookie_350=25110820'
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 检查响应状态
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"内容长度: {len(response.content)} 字节")
        
        # 如果响应成功
        if response.status_code == 200:
            print("请求成功!")
            
            # 保存响应内容到文件
            with open('response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("响应内容已保存到 response.html")
            
            # 显示响应内容的前500个字符
            print("\n响应内容预览:")
            print(response.text[:500])
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

def make_post_request():
    """
    发送POST请求到中南大学教务系统
    """
    # 请求URL
    url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
    
    # POST数据
    data = {
        'type': 'jg0101',
        'isview': '1',
        'zc': '',
        'xnxq01id': '2024-2025-2',
        'yxbh': '',
        'jszwdm': '',
        'teacherID': '宋力',
        'jg0101id': '0000197',
        'jg0101mc': '',
        'sfFD': '1'
    }
    
    # 请求头
    headers = {
        'Host': 'csujwc.its.csu.edu.cn',
        'Proxy-Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Origin': 'http://csujwc.its.csu.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': 'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_jg0101.jsp?xnxq01id=2024-2025-2&init=1&isview=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '_ga=GA1.1.2104536743.1742025470; _ga_PR7953H3X6=GS2.1.s1748770182$o51$g0$t1748770182$j60$l0$h0; JSESSIONID=A4C5E4CC52D43EFAA4A73B04E343FF57; SF_cookie_350=25110820'
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        # 检查响应状态
        print(f"POST请求状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"内容长度: {len(response.content)} 字节")
        
        # 如果响应成功
        if response.status_code == 200:
            print("POST请求成功!")
            
            # 保存响应内容到文件
            with open('post_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("POST响应内容已保存到 post_response.html")
            
            # 显示响应内容的前500个字符
            print("\nPOST响应内容预览:")
            print(response.text[:500])
            
        else:
            print(f"POST请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"POST请求发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    #print("开始发送请求到中南大学教务系统...")
    #print("\n=== GET请求 ===")
    #make_get_request()
    print("\n=== POST请求 ===")
    make_post_request()
