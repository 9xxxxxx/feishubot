import httpx

async def get_headers():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://httpbin.org/headers')
        print("发送的请求头：")
        print(response.request.headers)

# 运行异步函数
import asyncio
asyncio.run(get_headers())