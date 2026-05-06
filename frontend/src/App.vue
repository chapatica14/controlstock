<template>
  <div id="app">

    <!-- Página de login (quando não autenticado) -->
    <LoginView v-if="!sessao.token" @autenticado="aoEntrar" />

    <!-- Dashboard (quando autenticado) -->
    <template v-else>

      <!-- ═══════════════════════════════════════ -->
      <!--  BARRA DE TOPO                          -->
      <!-- ═══════════════════════════════════════ -->
      <header class="topbar">
        <div class="topbar-inner">

          <div class="logo">
            <span>📦</span>
            <div>
              <strong>ControloStock</strong>
              <small>Inventário de Produtos</small>
            </div>
          </div>

          <div class="topbar-stats">
            <div class="kpi">
              <span class="kpi-valor">{{ produtos.length }}</span>
              <span class="kpi-rotulo">Produtos</span>
            </div>
            <div class="kpi">
              <span class="kpi-valor">{{ totalUnidades }}</span>
              <span class="kpi-rotulo">Unidades</span>
            </div>
            <div class="kpi">
              <span class="kpi-valor">{{ totalValor }}</span>
              <span class="kpi-rotulo">Total (MT)</span>
            </div>
          </div>

          <div class="topbar-user">
            <span class="user-badge">👤 {{ sessao.nome }}</span>
            <button class="btn-sair" @click="sair">Sair</button>
          </div>

        </div>
      </header>

      <!-- ═══════════════════════════════════════ -->
      <!--  CONTEÚDO PRINCIPAL                     -->
      <!-- ═══════════════════════════════════════ -->
      <main class="main">

        <!-- ── FORMULÁRIO ── -->
        <section class="card">
          <h2 class="card-titulo">
            {{ editandoId ? '✏️  Editar Produto' : '➕  Novo Produto' }}
          </h2>

          <div class="form-grid">
            <div class="field">
              <label>Nome do Produto</label>
              <input v-model="form.nome"      type="text"   placeholder="Ex: Arroz (5kg)" />
            </div>
            <div class="field">
              <label>Categoria</label>
              <input v-model="form.categoria" type="text"   placeholder="Ex: Alimentação" />
            </div>
            <div class="field">
              <label>Quantidade</label>
              <input v-model.number="form.quantidade" type="number" placeholder="0" min="0" />
            </div>
            <div class="field">
              <label>Preço Unitário (MT)</label>
              <input v-model.number="form.preco" type="number" placeholder="0.00" min="0" step="0.01" />
            </div>
          </div>

          <div class="form-acoes">
            <button class="btn btn-primario" @click="gravar">
              {{ editandoId ? 'Guardar Alterações' : 'Adicionar Produto' }}
            </button>
            <button v-if="editandoId" class="btn btn-secundario" @click="cancelar">
              Cancelar
            </button>
          </div>

          <p v-if="alerta.msg" :class="['alerta', alerta.tipo]">{{ alerta.msg }}</p>
        </section>

        <!-- ── FILTROS ── -->
        <section class="card card-filtros">
          <div class="filtros-linha">
            <div class="filtros-categorias">
              <span class="filtros-rotulo">Categoria:</span>
              <div class="chips">
                <button
                  v-for="cat in categorias"
                  :key="cat"
                  :class="['chip', { activo: filtro.categoria === cat }]"
                  @click="filtro.categoria = cat"
                >{{ cat }}</button>
              </div>
            </div>
            <input
              v-model="filtro.pesquisa"
              type="text"
              class="input-pesquisa"
              placeholder="🔍  Pesquisar..."
            />
          </div>
        </section>

        <!-- ── TABELA ── -->
        <section class="card">
          <div class="tabela-cabecalho">
            <h2 class="card-titulo" style="margin:0">📋  Produtos em Stock</h2>
            <span class="badge-contagem">{{ produtosFiltrados.length }} registo(s)</span>
          </div>

          <p v-if="loading" class="estado-msg">A carregar...</p>
          <p v-else-if="!produtosFiltrados.length" class="estado-msg">Nenhum produto encontrado.</p>

          <div v-else class="tabela-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nome</th>
                  <th>Categoria</th>
                  <th>Quantidade</th>
                  <th>Preço (MT)</th>
                  <th>Valor Total</th>
                  <th>Registo</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in produtosFiltrados" :key="p.id">
                  <td class="td-mono">{{ p.id }}</td>
                  <td class="td-nome">{{ p.nome }}</td>
                  <td><span class="tag-categoria">{{ p.categoria }}</span></td>
                  <td>
                    <span :class="['tag-stock', nivelStock(p.quantidade)]">
                      {{ p.quantidade }}
                    </span>
                  </td>
                  <td class="td-mono">{{ fmt(p.preco) }}</td>
                  <td class="td-mono td-total">{{ fmt(p.quantidade * p.preco) }}</td>
                  <td class="td-mono td-data">{{ fmtData(p.data_registo) }}</td>
                  <td>
                    <div class="acoes">
                      <button class="btn-acao editar"   @click="editar(p)"     title="Editar">✏️</button>
                      <button class="btn-acao eliminar" @click="apagar(p.id)"  title="Eliminar">🗑️</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </template>
  </div>
</template>

<script>
import LoginView from './Login.vue'

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default {
  name: 'App',
  components: { LoginView },

  data() {
    return {
      // Sessão do utilizador
      sessao: {
        token: localStorage.getItem('cs_token') || '',
        nome:  localStorage.getItem('cs_nome')  || ''
      },

      // Lista de produtos vinda da API
      produtos: [],
      loading:  false,

      // Filtros da tabela
      filtro: {
        pesquisa:  '',
        categoria: 'Todas'
      },

      // Formulário (adicionar / editar)
      editandoId: null,
      form: {
        nome:      '',
        categoria: '',
        quantidade: '',
        preco:     ''
      },

      // Mensagem de feedback
      alerta: { msg: '', tipo: '' }
    }
  },

  computed: {
    // Lista de categorias únicas para os chips de filtro
    categorias() {
      const unicas = [...new Set(this.produtos.map(p => p.categoria))].sort()
      return ['Todas', ...unicas]
    },

    // Produtos depois de aplicar os filtros
    produtosFiltrados() {
      return this.produtos.filter(p => {
        const catOk = this.filtro.categoria === 'Todas' || p.categoria === this.filtro.categoria
        const q     = this.filtro.pesquisa.toLowerCase()
        const txtOk = !q || p.nome.toLowerCase().includes(q) || p.categoria.toLowerCase().includes(q)
        return catOk && txtOk
      })
    },

    totalUnidades() {
      return this.produtos.reduce((s, p) => s + Number(p.quantidade), 0)
    },

    totalValor() {
      const v = this.produtos.reduce((s, p) => s + Number(p.quantidade) * Number(p.preco), 0)
      return this.fmt(v)
    }
  },

  mounted() {
    if (this.sessao.token) this.carregarProdutos()
  },

  methods: {
    // ── SESSÃO ──────────────────────────────────────

    aoEntrar({ token, nome }) {
      this.sessao = { token, nome }
      this.carregarProdutos()
    },

    async sair() {
      await fetch(`${API}/auth/logout`, {
        method:  'POST',
        headers: { Authorization: `Bearer ${this.sessao.token}` }
      }).catch(() => {})
      localStorage.removeItem('cs_token')
      localStorage.removeItem('cs_nome')
      this.sessao   = { token: '', nome: '' }
      this.produtos = []
    },

    // ── CABEÇALHOS HTTP ─────────────────────────────

    hdrs() {
      return {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${this.sessao.token}`
      }
    },

    // ── CRUD ────────────────────────────────────────

    async carregarProdutos() {
      this.loading = true
      try {
        const res = await fetch(`${API}/produtos`, { headers: this.hdrs() })
        if (res.status === 401) { this.sair(); return }
        this.produtos = await res.json()
      } catch {
        this.flash('Erro de ligação ao servidor.', 'erro')
      } finally {
        this.loading = false
      }
    },

    async gravar() {
      const { nome, categoria, quantidade, preco } = this.form
      if (!nome || !categoria || quantidade === '' || preco === '') {
        this.flash('Preenche todos os campos.', 'erro')
        return
      }
      try {
        if (this.editandoId) {
          await fetch(`${API}/produtos/${this.editandoId}`, {
            method: 'PUT', headers: this.hdrs(), body: JSON.stringify(this.form)
          })
          this.flash('Produto actualizado com sucesso.', 'sucesso')
          this.editandoId = null
        } else {
          await fetch(`${API}/produtos`, {
            method: 'POST', headers: this.hdrs(), body: JSON.stringify(this.form)
          })
          this.flash('Produto adicionado com sucesso.', 'sucesso')
        }
        this.limparForm()
        this.carregarProdutos()
      } catch {
        this.flash('Erro ao guardar. Tenta novamente.', 'erro')
      }
    },

    editar(produto) {
      this.editandoId = produto.id
      this.form = {
        nome:      produto.nome,
        categoria: produto.categoria,
        quantidade: produto.quantidade,
        preco:     produto.preco
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },

    cancelar() {
      this.editandoId = null
      this.limparForm()
    },

    async apagar(id) {
      if (!confirm('Confirmas a eliminação deste produto?')) return
      await fetch(`${API}/produtos/${id}`, { method: 'DELETE', headers: this.hdrs() })
      this.flash('Produto eliminado.', 'sucesso')
      this.carregarProdutos()
    },

    // ── UTILIDADES ──────────────────────────────────

    limparForm() {
      this.form = { nome: '', categoria: '', quantidade: '', preco: '' }
    },

    flash(msg, tipo) {
      this.alerta = { msg, tipo }
      setTimeout(() => { this.alerta = { msg: '', tipo: '' } }, 4000)
    },

    nivelStock(qty) {
      if (qty === 0)  return 'esgotado'
      if (qty < 10)   return 'baixo'
      return                 'normal'
    },

    fmt(val) {
      return Number(val).toLocaleString('pt-MZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },

    fmtData(d) {
      return d ? new Date(d).toLocaleDateString('pt-PT') : '—'
    }
  }
}
</script>

<style scoped>
/* ── TOPBAR ─────────────────────────────────────────── */
.topbar {
  background: #0d1526;
  border-bottom: 1px solid var(--borda);
  padding: .9rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}
.topbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.logo { display: flex; align-items: center; gap: .75rem; }
.logo span { font-size: 1.75rem; }
.logo strong {
  display: block;
  font-size: 1.15rem;
  font-weight: 700;
  background: linear-gradient(90deg, var(--cor-primaria), var(--cor-primaria-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.logo small { font-size: .68rem; color: var(--texto-fraco); display: block; }

.topbar-stats { display: flex; gap: 1.5rem; }
.kpi { text-align: center; }
.kpi-valor  { display: block; font-size: 1.2rem; font-weight: 700; color: var(--cor-primaria); font-family: var(--fonte-mono); }
.kpi-rotulo { font-size: .6rem; color: var(--texto-fraco); text-transform: uppercase; letter-spacing: .8px; }

.topbar-user { display: flex; align-items: center; gap: .6rem; }
.user-badge {
  font-size: .8rem;
  color: var(--texto-fraco);
  background: var(--bg-input);
  border: 1px solid var(--borda);
  padding: .3rem .75rem;
  border-radius: 20px;
}
.btn-sair {
  font-family: var(--fonte);
  font-size: .8rem;
  background: rgba(239,68,68,.1);
  border: 1px solid rgba(239,68,68,.3);
  color: #f87171;
  padding: .3rem .85rem;
  border-radius: 7px;
  cursor: pointer;
  transition: background .15s;
}
.btn-sair:hover { background: rgba(239,68,68,.2); }

/* ── MAIN ────────────────────────────────────────────── */
.main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── CARDS ───────────────────────────────────────────── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--borda);
  border-radius: 14px;
  padding: 1.75rem;
}
.card-filtros { padding: 1rem 1.75rem; }
.card-titulo {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: var(--texto);
}

/* ── FORMULÁRIO ─────────────────────────────────────── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .9rem;
}
.field { display: flex; flex-direction: column; gap: .35rem; }
.field label {
  font-size: .73rem;
  font-weight: 600;
  color: var(--texto-fraco);
  text-transform: uppercase;
  letter-spacing: .5px;
}
.field input,
.input-pesquisa {
  background: var(--bg-input);
  border: 1px solid var(--borda);
  color: var(--texto);
  padding: .72rem .9rem;
  border-radius: 8px;
  font-family: var(--fonte);
  font-size: .9rem;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
  width: 100%;
}
.field input:focus,
.input-pesquisa:focus {
  border-color: var(--cor-primaria);
  box-shadow: 0 0 0 3px rgba(16,185,129,.12);
}
.field input::placeholder,
.input-pesquisa::placeholder { color: var(--texto-fraco); }

.form-acoes { display: flex; gap: .75rem; margin-top: 1.1rem; }
.btn {
  padding: .68rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-family: var(--fonte);
  font-size: .875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all .2s;
}
.btn-primario {
  background: linear-gradient(135deg, var(--cor-primaria), var(--cor-primaria-2));
  color: #051009;
}
.btn-primario:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(16,185,129,.35); }
.btn-secundario {
  background: transparent;
  border: 1px solid var(--borda);
  color: var(--texto-fraco);
}
.btn-secundario:hover { border-color: var(--texto-fraco); color: var(--texto); }

.alerta {
  margin-top: .9rem;
  padding: .7rem 1rem;
  border-radius: 8px;
  font-size: .875rem;
  font-weight: 500;
}
.sucesso { background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.25); color: #34d399; }
.erro    { background: rgba(239,68,68,.1);  border: 1px solid rgba(239,68,68,.25);  color: #f87171; }

/* ── FILTROS ─────────────────────────────────────────── */
.filtros-linha {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.filtros-categorias { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.filtros-rotulo { font-size: .73rem; font-weight: 600; color: var(--texto-fraco); text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; }
.chip {
  padding: .28rem .85rem;
  border-radius: 20px;
  border: 1px solid var(--borda);
  background: var(--bg-input);
  color: var(--texto-fraco);
  font-family: var(--fonte);
  font-size: .78rem;
  cursor: pointer;
  transition: all .15s;
}
.chip.activo {
  background: rgba(16,185,129,.15);
  border-color: var(--cor-primaria);
  color: var(--cor-primaria-2);
  font-weight: 600;
}
.chip:hover:not(.activo) { border-color: var(--texto-fraco); color: var(--texto); }
.input-pesquisa { width: 220px; }

/* ── TABELA ─────────────────────────────────────────── */
.tabela-cabecalho {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}
.badge-contagem {
  font-size: .75rem;
  background: rgba(16,185,129,.1);
  border: 1px solid rgba(16,185,129,.2);
  color: var(--cor-primaria-2);
  padding: .2rem .7rem;
  border-radius: 20px;
}
.tabela-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  padding: .65rem .9rem;
  font-size: .68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: var(--texto-fraco);
  border-bottom: 1px solid var(--borda);
}
td {
  padding: .82rem .9rem;
  font-size: .875rem;
  color: var(--texto);
  border-bottom: 1px solid rgba(30,45,69,.4);
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,.02); }

.td-nome  { font-weight: 600; }
.td-mono  { font-family: var(--fonte-mono); font-size: .82rem; }
.td-data  { color: var(--texto-fraco); }
.td-total { color: var(--cor-primaria-2); font-weight: 600; }

.tag-categoria {
  background: rgba(59,130,246,.1);
  border: 1px solid rgba(59,130,246,.2);
  color: #60a5fa;
  padding: .18rem .65rem;
  border-radius: 20px;
  font-size: .77rem;
  white-space: nowrap;
}
.tag-stock {
  font-family: var(--fonte-mono);
  font-weight: 600;
  padding: .18rem .55rem;
  border-radius: 6px;
  font-size: .82rem;
}
.normal   { background: rgba(16,185,129,.1); color: #34d399; }
.baixo    { background: rgba(245,158,11,.1); color: #f59e0b; }
.esgotado { background: rgba(239,68,68,.1);  color: #f87171; }

.acoes { display: flex; gap: .4rem; }
.btn-acao {
  background: none;
  border: 1px solid var(--borda);
  border-radius: 6px;
  padding: .28rem .5rem;
  cursor: pointer;
  font-size: .9rem;
  transition: all .15s;
}
.btn-acao.editar:hover   { border-color: var(--cor-primaria); background: rgba(16,185,129,.1); }
.btn-acao.eliminar:hover { border-color: var(--cor-erro);     background: rgba(239,68,68,.1);  }

.estado-msg { text-align: center; padding: 2.5rem; color: var(--texto-fraco); }

/* ── RESPONSIVO ─────────────────────────────────────── */
@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .main      { padding: 1rem; }
  .topbar-stats { gap: .75rem; }
  .input-pesquisa { width: 100%; }
}
</style>
