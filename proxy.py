# Contenuto esistente di proxy.py
import requests
from fp.fp import FreeProxy
import logging

# Ottieni una referenza al logger 'app_logger'
app_logger = logging.getLogger("app_logger")

def use_proxy(num_iterations=20):
    for i in range(num_iterations):
        try:
            proxy_obj = FreeProxy(rand=True)
            proxy_str = proxy_obj.get()
            response = requests.get('https://www.google.com/', proxies={'http': proxy_str, 'https': proxy_str}, verify=False, timeout=5)
            if response.status_code == 200:
                app_logger.info(f"***** Proxy funzionante trovato: {proxy_str} *****")
                return proxy_str
        except requests.RequestException as e:
            app_logger.info(f"Errore con proxy {proxy_str}: {e}")
    app_logger.info("Nessun proxy funzionante trovato.")
    return None

if __name__ == "__main__":
    use_proxy()