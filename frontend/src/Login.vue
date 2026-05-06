<template>
  <div class="pagina-login">

    <!-- Efeito de fundo decorativo -->
    <div class="fundo">
      <div class="circulo c1"></div>
      <div class="circulo c2"></div>
      <div class="circulo c3"></div>
    </div>

    <div class="cartao-login">

      <!-- Cabeçalho -->
      <div class="cabecalho">
        <span class="emoji-logo">📦</span>
        <h1>ControloStock</h1>
        <p>Sistema de Gestão de Produtos</p>
      </div>

      <!-- Abas de navegação -->
      <div class="abas">
        <button
          :class="['aba', { activa: aba === 'login' }]"
          @click="mudarAba('login')"
        >Entrar</button>
        <button
          :class="['aba', { activa: aba === 'registo' }]"
          @click="mudarAba('registo')"
        >Criar Conta</button>
      </div>

      <!-- ──────────────────────────────── -->
      <!--  FORMULÁRIO DE LOGIN             -->
      <!-- ──────────────────────────────── -->
      <form v-if="aba === 'login'" @submit.prevent="fazerLogin" novalidate>

        <div class="campo">
          <label>Utilizador ou Email</label>
          <div class="input-grupo">
            <span class="input-icone">👤</span>
            <input
              v-model="login.username"
              type="text"
              placeholder="ex: admin"
              autocomplete="username"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="campo">
          <label>Senha</label>
          <div class="input-grupo">
            <span class="input-icone">🔒</span>
            <input
              v-model="login.senha"
              :type="verSenha ? 'text' : 'password'"
              placeholder="••••••••"
              autocomplete="current-password"
              :disabled="loading"
            />
            <button type="button" class="btn-olho" @click="verSenha = !verSenha">
              {{ verSenha ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <p v-if="erro" class="msg-erro">{{ erro }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Entrar →</span>
        </button>

        <!-- Credenciais de demonstração -->
        <div class="demo">
          <span class="demo-titulo">Conta de demonstração</span>
          <div class="demo-linha">
            <span>Utilizador</span>
            <code @click="login.username = 'admin'">admin</code>
          </div>
          <div class="demo-linha">
            <span>Senha</span>
            <code @click="login.senha = 'admin123'">admin123</code>
          </div>
        </div>

        <p class="link-aba">
          Não tens conta?
          <a @click.prevent="mudarAba('registo')">Regista-te aqui</a>
        </p>

      </form>

      <!-- ──────────────────────────────── -->
      <!--  FORMULÁRIO DE REGISTO           -->
      <!-- ──────────────────────────────── -->
      <form v-if="aba === 'registo'" @submit.prevent="criarConta" novalidate>

        <div class="campo">
          <label>Nome Completo</label>
          <div class="input-grupo">
            <span class="input-icone">✍️</span>
            <input
              v-model="registo.nome"
              type="text"
              placeholder="Ex: João da Silva"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="campo">
          <label>Nome de Utilizador</label>
          <div class="input-grupo">
            <span class="input-icone">👤</span>
            <input
              v-model="registo.username"
              type="text"
              placeholder="Ex: goncalo123"
              autocomplete="username"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="campo">
          <label>Email</label>
          <div class="input-grupo">
            <span class="input-icone">📧</span>
            <input
              v-model="registo.email"
              type="email"
              placeholder="chapatica@email.com"
              autocomplete="email"
              :disabled="loading"
            />
          </div>
        </div>

        <div class="campo">
          <label>Senha <small>(mín. 6 caracteres)</small></label>
          <div class="input-grupo">
            <span class="input-icone">🔒</span>
            <input
              v-model="registo.senha"
              :type="verSenha ? 'text' : 'password'"
              placeholder="••••••••"
              autocomplete="new-password"
              :disabled="loading"
            />
            <button type="button" class="btn-olho" @click="verSenha = !verSenha">
              {{ verSenha ? '🙈' : '👁️' }}
            </button>
          </div>
          <!-- Indicador de força da senha -->
          <div v-if="registo.senha" class="forca-senha">
            <div class="forca-barra">
              <div :style="{ width: forca.pct + '%', background: forca.cor }"></div>
            </div>
            <span :style="{ color: forca.cor }">{{ forca.label }}</span>
          </div>
        </div>

        <p v-if="erro"    class="msg-erro">{{ erro }}</p>
        <p v-if="sucesso" class="msg-sucesso">{{ sucesso }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Criar Conta</span>
        </button>

        <p class="link-aba">
          Já tens conta?
          <a @click.prevent="mudarAba('login')">Entra aqui</a>
        </p>

      </form>

      <p class="rodape">Gonçalo junior</p>

    </div>
  </div>
</template>

<script>
const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default {
  name: 'LoginView',
  emits: ['autenticado'],

  data() {
    return {
      aba:     'login',   // aba activa: 'login' | 'registo'
      loading: false,
      verSenha: false,
      erro:    '',
      sucesso: '',
      login: {
        username: '',
        senha: ''
      },
      registo: {
        nome:     '',
        username: '',
        email:    '',
        senha:    ''
      }
    }
  },

  computed: {
    // Calcula a força da senha em tempo real
    forca() {
      const s = this.registo.senha
      let pts = 0
      if (s.length >= 6)       pts++
      if (s.length >= 10)      pts++
      if (/[A-Z]/.test(s))    pts++
      if (/[0-9]/.test(s))    pts++
      if (/[^A-Za-z0-9]/.test(s)) pts++

      const niveis = [
        { pct: 20,  cor: '#ef4444', label: 'Muito fraca' },
        { pct: 40,  cor: '#f97316', label: 'Fraca'       },
        { pct: 65,  cor: '#f59e0b', label: 'Razoável'    },
        { pct: 85,  cor: '#3b82f6', label: 'Boa'         },
        { pct: 100, cor: '#10b981', label: 'Forte'       }
      ]
      return niveis[Math.min(pts, 4)]
    }
  },

  methods: {
    mudarAba(novaAba) {
      this.aba     = novaAba
      this.erro    = ''
      this.sucesso = ''
    },

    async fazerLogin() {
      this.erro = ''
      if (!this.login.username || !this.login.senha) {
        this.erro = 'Preenche todos os campos.'
        return
      }
      this.loading = true
      try {
        const res  = await fetch(`${API}/auth/login`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(this.login)
        })
        const data = await res.json()
        if (!res.ok) { this.erro = data.erro; return }

        localStorage.setItem('cs_token', data.token)
        localStorage.setItem('cs_nome',  data.nome)
        this.$emit('autenticado', { token: data.token, nome: data.nome })
      } catch {
        this.erro = 'Sem ligação ao servidor. Verifica se o Docker está activo.'
      } finally {
        this.loading = false
      }
    },

    async criarConta() {
      this.erro    = ''
      this.sucesso = ''
      const { nome, username, email, senha } = this.registo

      if (!nome || !username || !email || !senha) {
        this.erro = 'Preenche todos os campos.'
        return
      }
      if (senha.length < 6) {
        this.erro = 'A senha precisa de ter pelo menos 6 caracteres.'
        return
      }
      this.loading = true
      try {
        const res  = await fetch(`${API}/auth/registo`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(this.registo)
        })
        const data = await res.json()
        if (!res.ok) { this.erro = data.erro; return }

        this.sucesso = data.mensagem
        const u = username
        this.registo = { nome: '', username: '', email: '', senha: '' }
        setTimeout(() => {
          this.login.username = u
          this.mudarAba('login')
        }, 2000)
      } catch {
        this.erro = 'Sem ligação ao servidor.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Página de login */
.pagina-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Círculos decorativos de fundo */
.fundo     { position: absolute; inset: 0; pointer-events: none; }
.circulo   { position: absolute; border-radius: 50%; filter: blur(90px); opacity: .08; animation: flutuar 10s ease-in-out infinite; }
.c1 { width: 500px; height: 500px; background: var(--cor-primaria);   top: -150px; left: -150px; animation-delay: 0s;  }
.c2 { width: 350px; height: 350px; background: var(--cor-info);       bottom: -100px; right: -100px; animation-delay: 4s;  }
.c3 { width: 250px; height: 250px; background: #8b5cf6; top: 55%; left: 55%; animation-delay: 7s;  }
@keyframes flutuar {
  0%, 100% { transform: translateY(0)    scale(1);    }
  50%       { transform: translateY(-30px) scale(1.05); }
}

/* Cartão central */
.cartao-login {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 430px;
  background: var(--bg-card);
  border: 1px solid var(--borda);
  border-radius: 20px;
  padding: 2.25rem 2.5rem;
  box-shadow: 0 24px 60px rgba(0, 0, 0, .5);
}

/* Cabeçalho */
.cabecalho      { text-align: center; margin-bottom: 1.75rem; }
.emoji-logo     { font-size: 2.5rem; display: block; margin-bottom: .5rem; }
.cabecalho h1   {
  font-size: 1.65rem;
  font-weight: 700;
  background: linear-gradient(90deg, var(--cor-primaria), var(--cor-primaria-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: .2rem;
}
.cabecalho p    { font-size: .8rem; color: var(--texto-fraco); }

/* Abas */
.abas {
  display: flex;
  background: var(--bg-input);
  border-radius: 10px;
  padding: 3px;
  margin-bottom: 1.5rem;
}
.aba {
  flex: 1;
  padding: .55rem;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--texto-fraco);
  font-family: var(--fonte);
  font-size: .875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background .2s, color .2s;
}
.aba.activa {
  background: var(--bg-card);
  color: var(--texto);
  box-shadow: 0 1px 4px rgba(0,0,0,.4);
}

/* Campos */
.campo        { margin-bottom: 1rem; }
.campo label  {
  display: block;
  font-size: .75rem;
  font-weight: 600;
  color: var(--texto-fraco);
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-bottom: .35rem;
}
.campo label small {
  font-size: .7rem;
  text-transform: none;
  font-weight: 400;
  letter-spacing: 0;
}
.input-grupo  { position: relative; display: flex; align-items: center; }
.input-icone  { position: absolute; left: .85rem; font-size: .9rem; pointer-events: none; }
.input-grupo input {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--borda);
  color: var(--texto);
  padding: .78rem 1rem .78rem 2.6rem;
  border-radius: 9px;
  font-family: var(--fonte);
  font-size: .925rem;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
}
.input-grupo input:focus {
  border-color: var(--cor-primaria);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, .12);
}
.input-grupo input::placeholder { color: var(--texto-fraco); }
.input-grupo input:disabled { opacity: .5; cursor: not-allowed; }
.btn-olho {
  position: absolute;
  right: .7rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: .9rem;
  padding: .2rem;
  line-height: 1;
}

/* Força da senha */
.forca-senha { display: flex; align-items: center; gap: .6rem; margin-top: .4rem; }
.forca-barra { flex: 1; height: 3px; background: var(--borda); border-radius: 2px; overflow: hidden; }
.forca-barra div { height: 100%; border-radius: 2px; transition: width .3s, background .3s; }
.forca-senha span { font-size: .7rem; font-weight: 600; min-width: 70px; }

/* Mensagens */
.msg-erro    { color: #f87171; font-size: .85rem; margin-bottom: .75rem; }
.msg-sucesso { color: var(--cor-primaria-2); font-size: .85rem; margin-bottom: .75rem; }

/* Botão principal */
.btn-submit {
  width: 100%;
  padding: .85rem;
  margin-bottom: 1rem;
  border: none;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--cor-primaria), var(--cor-primaria-2));
  color: #051009;
  font-family: var(--fonte);
  font-size: .95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .5rem;
  transition: opacity .2s, transform .2s, box-shadow .2s;
}
.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, .35);
}
.btn-submit:disabled { opacity: .55; cursor: not-allowed; transform: none; }

/* Spinner */
.spinner {
  width: 17px; height: 17px;
  border: 2px solid rgba(0,0,0,.2);
  border-top-color: #051009;
  border-radius: 50%;
  animation: girar .65s linear infinite;
}
@keyframes girar { to { transform: rotate(360deg); } }

/* Demo */
.demo {
  background: var(--bg-input);
  border: 1px dashed var(--borda);
  border-radius: 9px;
  padding: .85rem 1rem;
  margin-bottom: 1rem;
}
.demo-titulo { display: block; font-size: .7rem; font-weight: 600; color: var(--texto-fraco); text-transform: uppercase; letter-spacing: .5px; margin-bottom: .45rem; }
.demo-linha { display: flex; justify-content: space-between; align-items: center; font-size: .82rem; color: var(--texto-fraco); margin-bottom: .3rem; }
.demo-linha:last-child { margin-bottom: 0; }
.demo-linha code {
  background: rgba(16,185,129,.1);
  color: var(--cor-primaria-2);
  padding: .1rem .5rem;
  border-radius: 5px;
  font-family: var(--fonte-mono);
  font-size: .8rem;
  cursor: pointer;
  user-select: none;
}
.demo-linha code:hover { background: rgba(16,185,129,.2); }

/* Link entre abas */
.link-aba { text-align: center; font-size: .83rem; color: var(--texto-fraco); }
.link-aba a { color: var(--cor-primaria-2); cursor: pointer; font-weight: 600; }
.link-aba a:hover { text-decoration: underline; }

/* Rodapé */
.rodape { text-align: center; font-size: .68rem; color: var(--texto-fraco); margin-top: 1.5rem; opacity: .5; }

@media (max-width: 480px) {
  .cartao-login { padding: 1.75rem 1.25rem; }
}
</style>
