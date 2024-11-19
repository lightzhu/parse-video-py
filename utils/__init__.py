from urllib.parse import parse_qs, urlparse
import requests

def get_val_from_url_by_query_key(url: str, query_key: str) -> str:
    """
    从url的query参数中解析出query_key对应的值
    :param url: url地址
    :param query_key: query参数的key
    :return:
    """
    url_res = urlparse(expand_short_url(url))
    url_query = parse_qs(url_res.query, keep_blank_values=True)

    try:
        query_val = url_query[query_key][0]
    except KeyError:
        raise KeyError(f"url中不存在query参数: {query_key}")

    if len(query_val) == 0:
        raise ValueError(f"url中query参数值长度为0: {query_key}")

    return url_query[query_key][0]

def expand_short_url(short_url: str) -> str:
    """
    将短链接转换为原始链接。
    :param short_url: 短链接
    :return: 原始链接
    """
    try:
        # 设置请求头部
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # 发送HEAD请求，允许重定向
        response = requests.head(short_url, allow_redirects=True, headers=headers, timeout=10)
        response.raise_for_status()

        # 返回最终的URL
        return response.url
    except requests.RequestException as e:
        print(f"Error expanding URL: {e}")
        return None