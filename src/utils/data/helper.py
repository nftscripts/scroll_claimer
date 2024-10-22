with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
    private_keys = [line.strip() for line in file]


with open('recipients.txt', 'r', encoding='utf-8-sig') as file:
    recipients = [line.strip() for line in file]


with open('proxies.txt', 'r', encoding='utf-8-sig') as file:
    proxies = [line.strip() for line in file]
    if not proxies:
        proxies = [None for _ in range(len(private_keys))]