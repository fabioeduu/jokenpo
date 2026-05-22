# Jogo de Jokenpô em Python com Deploy no Azure

Este repositório contém um jogo simples de **jokenpô** (pedra, papel e tesoura) desenvolvido em Python, juntamente com um **Dockerfile** para containerizar a aplicação e um workflow do **GitHub Actions** para realizar o deploy no **Azure Container Instances (ACI)**.

## Funcionalidades do Jogo
- Jogue quantas rodadas quiser contra o computador.
- O jogo mantém um placar das vitórias de cada lado.
- Digite **"SAIR"** para encerrar o jogo e visualizar o placar final.

## Pré-requisitos
- Python 3.9 ou superior.
- Docker instalado.
- Conta no Azure com um **Azure Container Registry (ACR)** configurado.
- **GitHub Secrets** configurados:
  - `AZURE_CREDENTIALS`: Credenciais de serviço do Azure em formato JSON.
  - `REGISTRY_LOGIN_SERVER`: Nome do seu ACR (ex: `meuacr.azurecr.io`).
  - `REGISTRY_USERNAME`: Usuário do ACR.
  - `REGISTRY_PASSWORD`: Senha do ACR.
  - `RESOURCE_GROUP`: Nome do grupo de recursos do Azure.
  - `LOCATION`: Região do Azure (ex: `eastus`).

## Configurando o Projeto

## Feito para checkpoint devops 03

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/jokenpo-azure.git
cd jokenpo-azure


