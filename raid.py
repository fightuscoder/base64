import aiohttp
import asyncio
import time
import os
from colorama import Fore, init
import base64
import datetime
init()

BUILD = "v1.22"
news = "Updated: Batch ranking (300 per cycle) now only counts successful/attempted ranks, ignores skips."

def pause():
    os.system("pause")

os.system("title Arxan :: Roblox Group Nuker")

# KEY SYSTEM
#########################################################################################################################

ENC_URL = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2ZpZ2h0dXNjb2Rlci9iYXNlNjQvcmVmcy9oZWFkcy9tYWluL2tleS50eHQ="
def get_url():
    return base64.b64decode(ENC_URL).decode()

# WEBHOOK LOGGER
WEBHOOK = "https://discord.com/api/webhooks/1443425073066414183/RC1Q5G7aEP-15G620m5EqVpmMdJf4hBvIvDiqq0rt-5aQML0cMg6NlJhXZKg9y7LbaWI"

async def log_key(k):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "content": f"\n==============\n**KEY USED - ARXAN NUKER | {BUILD}**\n`{k}`\n`{ts}`\n=============="
    }
    async with aiohttp.ClientSession() as s:
        await s.post(WEBHOOK, json=data)

async def check_key():
    url = get_url()
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            keys = (await r.text()).splitlines()

    k = input(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + " | Enter the key >>> ")
    print()

    if k not in keys:
        print(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + " | Invalid key passed.")
        print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + " | Exiting in three seconds...")
        time.sleep(3)
        exit()

    # log key here
    await log_key(k)

########################################################################################################################
RATE_LIMIT = 45
ERROR_LIMIT = 100

banner = '''
 █████  ██████  ██  ██  █████  ███    ██ 
██   ██ ██   ██  ██ ██  ██   ██ ████   ██ 
███████ ██████   ███   ███████ ██ ██  ██ 
██   ██ ██   ██  ██ ██  ██   ██ ██  ██ ██ 
██   ██ ██   ██ ██  ██ ██   ██ ██   ████ 
                                         '''  

#############################################################################
async def get_csrf(session):
    async with session.post('https://auth.roblox.com/v2/logout') as r:
        if r.status == 403:
            return r.headers.get('x-csrf-token')
        raise Exception(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + " | Cannot get CSRF token")

async def get_bot(session):
    async with session.get('https://users.roblox.com/v1/users/authenticated') as r:
        js = await r.json()
        return js['id']

async def get_rank(session, uid, group):
    async with session.get(f'https://groups.roblox.com/v1/users/{uid}/groups/roles') as r:
        js = await r.json()
        for g in js['data']:
            if g['group']['id'] == group:
                return g['role']['rank']
    return None

async def get_role_id(session, group, name):
    async with session.get(f'https://groups.roblox.com/v1/groups/{group}/roles') as r:
        js = await r.json()
        for x in js['roles']:
            if x['name'].lower() == name.lower():
                return x['id']
    raise Exception(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + " | Role not found")

async def change_role(session, user, group, bot_rank, role_id, role_name, counters):
    if counters['errors'] >= ERROR_LIMIT:
        return False

    uid = user['user']['userId']
    uname = user['user']['username']
    urank = user['role']['rank']

    if urank >= bot_rank:
        print(Fore.CYAN + "(ARXAN)" + Fore.YELLOW + " [SKIP]" + Fore.WHITE + f" | Skipping {uname} due to same or higher rank.")
        return False

    if user['role']['id'] == role_id:
        return False

    while True:
        async with session.patch(f'https://groups.roblox.com/v1/groups/{group}/users/{uid}', json={'roleId': role_id}) as r:

            if r.status == 429:
                print(Fore.CYAN + "(ARXAN)" + Fore.YELLOW + " [WARN]" + Fore.WHITE + f" | We are being ratelimited, waiting {RATE_LIMIT}...")
                await asyncio.sleep(RATE_LIMIT)
                continue

            if 500 <= r.status < 600:
                print(Fore.CYAN + "(ARXAN)" + Fore.YELLOW + " [WARN]" + Fore.WHITE + f" | Server error {r.status} on {uname}, retrying...")
                await asyncio.sleep(2)
                continue

            if r.status == 401 or r.status == 403:
                print(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + f" | Cannot rank {uname}, most likely no access.")
                return True

            if r.status >= 400:
                counters['errors'] += 1
                print(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + f" | HTTP error {r.status} on {uname}")
                return True

            counters['success'] += 1
            print(Fore.CYAN + "(ARXAN)" + Fore.GREEN + " [PASS]" + Fore.WHITE + f" | Ranked {uname} to {role_name}")
            return True

####################################################################################

async def main():
    await check_key()
    print(Fore.CYAN + "(ARXAN)" + Fore.GREEN + " [PASS]" + Fore.WHITE + " | Valid key passed.")
    print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + " | Testing Roblox API...")

    try:
        times = []
        url = "https://users.roblox.com/v1/users/1"
        for _ in range(5):
            t1 = time.perf_counter()
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r:
                    if r.status != 200:
                        print(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + " | Can connect to Roblox: " + Fore.RED + "FAIL")
                        pause()
                        return
            t2 = time.perf_counter()
            times.append((t2 - t1) * 1000)

        avg = sum(times) / len(times)
        print(Fore.CYAN + "(ARXAN)" + Fore.GREEN + " [PASS]" + Fore.WHITE + " | Can connect to Roblox: " + Fore.GREEN + "PASS")
        print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + f" | Roblox API average response time: {avg:.0f}ms")

    except:
        print(Fore.CYAN + "(ARXAN)" + Fore.RED + " [FAIL]" + Fore.WHITE + " | Can connect to Roblox: " + Fore.RED + "FAIL")
        pause()
        return

    print()
    print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + f" | Continuing in three seconds...")
    time.sleep(3)
    os.system("cls")
    print(Fore.CYAN + banner)
    print(Fore.WHITE + "by " + Fore.RED + "syphoncore" + Fore.WHITE + " company")
    print(Fore.WHITE + f"Build: {BUILD}")
    print(Fore.WHITE + f"News: {news}")
    print("\n")

    cookie = input(Fore.CYAN + "(ARXAN)" + Fore.WHITE + " | Input Roblox Cookie >>> ")
    group = int(input(Fore.CYAN + "(ARXAN)" + Fore.WHITE + " | Input Group ID >>> "))
    rank_name = input(Fore.CYAN + "(ARXAN)" + Fore.WHITE + " | Input Group Rank >>> ")
    os.system("cls")

    headers = {
        'Cookie': f'.ROBLOSECURITY={cookie}',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        csrf = await get_csrf(session)
        session.headers['X-CSRF-TOKEN'] = csrf

        target_role = await get_role_id(session, group, rank_name)
        bot = await get_bot(session)
        bot_rank = await get_rank(session, bot, group)

        counters = {'errors': 0, 'success': 0}
        cursor = None
        batch_counter = 0
        
        print(Fore.CYAN + "(ARXAN)" + Fore.LIGHTMAGENTA_EX + " [SCANNER]" + Fore.WHITE + " | Starting batched ranking process...")

        while True:
            params = {'limit': '100'}
            if cursor:
                params['cursor'] = cursor

            async with session.get(f'https://groups.roblox.com/v1/groups/{group}/users', params=params) as r:
                if r.status != 200:
                    print(Fore.RED + " [!] Failed to fetch user page, retrying...")
                    await asyncio.sleep(5)
                    continue
                
                js = await r.json()
                users_on_page = js['data']
                
                # Rank current page users
                tasks = []
                for u in users_on_page:
                    tasks.append(asyncio.create_task(
                        change_role(session, u, group, bot_rank, target_role, rank_name, counters)
                    ))
                
                # We collect results to see how many were actually ranked (True) vs skipped (False)
                results = await asyncio.gather(*tasks)
                
                # Only add to batch_counter if change_role returned True
                batch_counter += sum(1 for x in results if x is True)
                
                cursor = js.get('nextPageCursor')

                # Check if we hit the 300 limit based ONLY on ranking actions
                if batch_counter >= 300:
                    print(Fore.CYAN + "(ARXAN)" + Fore.YELLOW + " [BATCH]" + Fore.WHITE + f" | {batch_counter} users ranked. Resting for {RATE_LIMIT}s to prevent ratelimit...")
                    await asyncio.sleep(RATE_LIMIT)
                    batch_counter = 0 # Reset batch tracker

                if not cursor or counters['errors'] >= ERROR_LIMIT:
                    break

        print()
        print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + f" | Ranking complete, ranked a total of {counters['success']} users")
        print(Fore.CYAN + "(ARXAN)" + Fore.BLUE + " [INFO]" + Fore.WHITE + f" | Total Errors: {counters['errors']}")
        pause()

if __name__ == "__main__":
    asyncio.run(main())
