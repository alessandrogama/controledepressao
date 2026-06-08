"""
cep_service.py — Serviço isolado para consulta de CEP via API ViaCEP.
"""

import urllib.request
import urllib.error
import json

def consultar_cep(cep: str) -> dict | None:
    """
    Consulta o CEP informado utilizando a API pública do ViaCEP.
    Retorna um dicionário com os dados do endereço se encontrado, ou None se:
    - O CEP for inválido/mal formatado.
    - O CEP não for localizado (não existente).
    - Ocorrer um erro de rede, HTTP ou timeout.

    Garante um timeout máximo de 3 segundos e trata todas as exceções.
    """
    # Remove caracteres não numéricos
    cep_limpo = "".join(char for char in cep if char.isdigit())

    if len(cep_limpo) != 8:
        return None

    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ControleDepressaoApp/1.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                
                # ViaCEP retorna {"erro": "true"} ou {"erro": True} quando o CEP não é encontrado
                if data.get("erro") in (True, "true"):
                    return None

                return {
                    "rua": data.get("logradouro", "").strip(),
                    "bairro": data.get("bairro", "").strip(),
                    "cidade": data.get("localidade", "").strip(),
                    "estado": data.get("uf", "").strip(),
                    "complemento": data.get("complemento", "").strip(),
                }
    except Exception:
        # Silencia todas as exceções de rede/timeout/HTTP e retorna None (requisito de resiliência)
        return None
