# ControloStock

**Sistema de Gestão de Produtos** · INFC-0015 – Computação na Nuvem  
Gonçalo Chapatica · Licenciatura em Informática · 3.º Ano · UTDEG · 2026

---

## Arquitectura (3 Camadas)

```
Browser
  │
  ▼
Frontend  (Vue.js 3 + Vite + Nginx)   → porta 80
  │  HTTP / JSON
  ▼
Backend   (Python 3.11 + Flask)        → porta 5000
  │  SQL
  ▼
Base de Dados  (MySQL 8.0)             → porta 3306
```

## Stack Tecnológico

| Camada       | Tecnologia               |
|--------------|--------------------------|
| Frontend     | Vue.js 3, Vite, Nginx    |
| Backend      | Python 3.11, Flask       |
| Base de Dados| MySQL 8.0                |
| Infra        | Docker, Docker Compose   |

## Executar Localmente

```bash
# 1.   extrair o projecto
cd controlstock

# 2. Construir imagens e iniciar containers
docker compose up --build

# 3. Abrir no browser
http://localhost
```

## Credenciais de Demonstração

| Campo      | Valor      |
|------------|------------|
| Utilizador | admin      |
| Senha      | admin123   |

## Endpoints da API

| Método | Rota                 | Descrição            |
|--------|----------------------|----------------------|
| POST   | /auth/registo        | Criar conta          |
| POST   | /auth/login          | Fazer login          |
| POST   | /auth/logout         | Terminar sessão      |
| GET    | /produtos            | Listar produtos      |
| POST   | /produtos            | Criar produto        |
| PUT    | /produtos/:id        | Actualizar produto   |
| DELETE | /produtos/:id        | Eliminar produto     |

## Comandos Docker Úteis

```bash
docker compose up --build     # inicia (primeira vez)
docker compose up -d          # inicia em background
docker compose down           # para todos os containers
docker compose logs -f        # ver logs em tempo real
docker compose ps             # estado de cada container
docker compose down -v        # apaga também os volumes (reset BD)
```

## Estrutura do Projecto

```
controlstock/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── Login.vue
│       └── assets/
│           └── main.css
└── database/
    └── init.sql
```
