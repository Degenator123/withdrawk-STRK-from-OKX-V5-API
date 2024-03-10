import time
import random
import hmac
import base64
import requests
import json

#----API Credentials----#
okx_apikey = "INSERT API KEY "
okx_apisecret = "INSERT API SECRET"
okx_passphrase = "INSERT PASSWORD"

#----Withdrawal Settings----#
currency = "ETH"  # Example currency
chain = "ETH-Starknet"  # Example chain for the currency
amount_range = [0.001, 0.001]  # Minimum and maximum amount to withdraw
fee = "0.001"  # Example fee, adjust based on actual requirements

#----Operational Settings----#
delay_range = [1, 5]  # Minimum and maximum delay between withdrawals
shuffle_wallets = "no"  # Whether to shuffle wallets ("yes" / "no")

def get_iso_time():
    return time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())

def signature_v5(timestamp, method, request_path, body, secret_key):
    message = timestamp + method + request_path + (json.dumps(body) if body else '')
    mac = hmac.new(bytes(secret_key, 'utf-8'), bytes(message, 'utf-8'), digestmod='sha256')
    return base64.b64encode(mac.digest()).decode()

def get_header_v5(api_key, passphrase, secret_key, method, request_path, body=None):
    timestamp = get_iso_time()
    sign = signature_v5(timestamp, method, request_path, body, secret_key)
    return {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': sign,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }

def okx_withdraw_v5(currency, amount, destination, chain, fee):
    method = 'POST'
    request_path = '/api/v5/asset/withdrawal'
    body = {
        "ccy": currency,
        "amt": str(amount),
        "dest": "4",  # on-chain withdrawal
        "toAddr": destination,
        "fee": fee,
        "chain": chain
    }
    headers = get_header_v5(okx_apikey, okx_passphrase, okx_apisecret, method, request_path, body)
    
    url = 'https://www.okex.com' + request_path
    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()


def shuffle_wallets_if_needed(wallets_list):
    if shuffle_wallets.lower() == "yes":
        random.shuffle(wallets_list)
    return wallets_list

if __name__ == "__main__":
    with open("wallets.txt", "r") as f:
        wallets_list = [row.strip() for row in f if row.strip()]
        wallets_list = shuffle_wallets_if_needed(wallets_list)
        print(f'Number of wallets: {len(wallets_list)}')

        for wallet_number, address in enumerate(wallets_list, start=1):
            amount_to_withdraw = random.uniform(amount_range[0], amount_range[1])
            response = okx_withdraw_v5(currency, amount_to_withdraw, address, chain, fee)
            print(f'\n>>>[OKx] Withdrawal response for wallet {wallet_number}:', response)
            time.sleep(random.randint(delay_range[0], delay_range[1]))
