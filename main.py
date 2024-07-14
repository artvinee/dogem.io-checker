import aiohttp
import asyncio
from aiohttp_socks import ProxyConnector

USE_PROXY = True
TYPE_PROXY = 'socks5'  # http, https or socks5


def um(t):
    t = t.lower()
    e = 0
    for char in t:
        if char == '0':
            r = 86
        elif char == 'x':
            r = 99
        elif char == 'a':
            r = 75
        elif char == 'b':
            r = 83
        elif char == 'c':
            r = 25
        elif char == 'd':
            r = 64
        elif char == 'e':
            r = 87
        elif char == 'f':
            r = 91
        else:
            r = int(char) if char.isdigit() else ord(char)
        e += r
    return e


async def send_request(wallet, proxy):
    url = "https://dogem.io/ajax_check_wallet.php"
    payload = {
        "hash": str(um(wallet)),
        "wallet": wallet
    }

    header = {
        "Referer": "https://dogem.io/?ref=0x9eBC92adB03Eaee05d90de9eab4C4ae820bB04bD"  # dont remove pls
    }
    
    if USE_PROXY:
        if not proxy.startswith(('http://', 'https://', 'socks5://')):
            proxy = f"{TYPE_PROXY}://{proxy}"

        if TYPE_PROXY == 'socks5':
            connector = ProxyConnector.from_url(proxy)
            proxy_for_request = None
        elif TYPE_PROXY == 'http':
            connector = aiohttp.TCPConnector()
            proxy_for_request = proxy
        else:
            print(f"Unsupported type of proxy: {TYPE_PROXY}")
            return
    else:
        connector = aiohttp.TCPConnector()
        proxy_for_request = None

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, data=payload, proxy=proxy_for_request, timeout=30, headers=header) as response:
                if response.status == 200:
                    r = await response.json()
                    if r['status'] == "eligible":
                        print(f"Wallet {wallet} is eligible!")
                    else:
                        print(f"Wallet {wallet} is NOT eligible.")
                else:
                    print(f"Error for wallet {wallet}: HTTP {response.status}")
    except Exception as e:
        print(f"Error for wallet {wallet}: {str(e)}")


async def main():
    with open('wallets.txt', 'r') as f:
        wallets = f.read().splitlines()

    if USE_PROXY:
        with open('proxies.txt', 'r') as f:
            proxies = f.read().splitlines()
        if len(proxies) < len(wallets):
            print("Not enough proxies!")
            return
    else:
        proxies = [None] * len(wallets)

    tasks = []
    for wallet, proxy in zip(wallets, proxies):
        task = asyncio.create_task(send_request(wallet, proxy))
        tasks.append(task)
        await asyncio.sleep(2)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
