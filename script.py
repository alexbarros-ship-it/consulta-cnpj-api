import urllib.request
import urllib.error
import re
import json
import unicodedata

class ConsultorCNPJ:
    def __init__(self):
        self.api_key = "667c7881-0aef-4f63-a109-6b296b94ea6f-6934c548-32ee-4a32-bc10-fead09e6dc4a"
        self.base_url = "https://api.cnpja.com/office/"
        self.headers = {'Authorization': self.api_key}

    def remover_acentos(self, texto):
        if not texto:
            return ""
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()

    def formatar_cnpj(self, cnpj_limpo):
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    def consultar(self, cnpj_input):
        cnpj_limpo = re.sub(r'\D', '', cnpj_input)
        
        if len(cnpj_limpo) != 14:
            print("⚠️ Erro: Insira um CNPJ válido com 14 dígitos.")
            return

        cnpj_formatado = self.formatar_cnpj(cnpj_limpo)
        todos_estados = "AC,AL,AM,AP,BA,CE,DF,ES,GO,MA,MG,MS,MT,PA,PB,PE,PI,PR,RJ,RN,RO,RR,RS,SC,SE,SP,TO"
        url = f"{self.base_url}{cnpj_limpo}?registrations={todos_estados}"

        print(f"\n⏳ Consultando dados do CNPJ {cnpj_formatado}...")

        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as response:
                dados = json.loads(response.read().decode('utf-8'))
                
                nome_empresa = dados.get('company', {}).get('name', 'N/A')
                
                print("\n" + "="*105)
                print(f"🏢 EMPRESA : {nome_empresa}")
                print(f"📌 CNPJ    : {cnpj_formatado}")
                print("="*105)

                todas_ies_raw = dados.get('registrations', [])
                
                # =========================================================
                # FILTRO ANTI-NULL
                # Remove itens onde 'number' é None, string vazia ou "null"
                # =========================================================
                todas_ies_validas = [
                    ie for ie in todas_ies_raw 
                    if ie.get('number') is not None 
                    and str(ie.get('number')).strip() != '' 
                    and str(ie.get('number')).strip().lower() != 'null'
                ]
                
                if todas_ies_validas:
                    # Ordena alfabeticamente pela UF
                    todas_ies_validas = sorted(todas_ies_validas, key=lambda x: x.get('state', ''))
                    
                    print(f"📜 INSCRIÇÕES ESTADUAIS VÁLIDAS ({len(todas_ies_validas)} registro(s)):")
                    print("-" * 105)
                    print(f"{'UF':<4} | {'NÚMERO DA IE':<15} | {'SITUAÇÃO':<10} | {'TIPO DE INSCRIÇÃO':<32} | {'STATUS NA SEFAZ'}")
                    print("-" * 105)
                    
                    for ie in todas_ies_validas:
                        estado = ie.get('state', 'UF')
                        numero = ie.get('number', 'S/N')
                        tipo_original = ie.get('type', {}).get('text', 'Não definido')
                        status_texto = ie.get('status', {}).get('text', 'Sem informação')
                        situacao = "ATIVA" if ie.get('enabled') else "INATIVA"
                        
                        tipo_limpo = self.remover_acentos(tipo_original)
                        eh_alvo = ('normal' in tipo_limpo or 'substituto' in tipo_limpo or 'outra uf' in tipo_limpo or 'outro estado' in tipo_limpo)
                        marcador = "[✓] " if eh_alvo else "[ ] "
                        
                        print(f"[{estado}] | {numero:<15} | {situacao:<10} | {marcador + tipo_original:<32} | {status_texto}")
                else:
                    print("⚠️  A API não retornou NENHUMA Inscrição Estadual válida para este CNPJ.")
                
                print("="*105 + "\n")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"❌ Erro 404: CNPJ não encontrado na base de dados.\n")
            else:
                print(f"❌ Erro HTTP {e.code} ao consultar a API.\n")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}\n")

# ==========================================
# EXECUTAR SCRIPT
# ==========================================
if __name__ == "__main__":
    consultor = ConsultorCNPJ() 
    consultor.consultar("07.526.557/0116-59")