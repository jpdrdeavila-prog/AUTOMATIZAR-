import { useEffect, useState } from 'react';
import { Activity, ArrowUpRight, Bot, CircleCheck, Clock3, Layers3, ShieldCheck, Zap } from 'lucide-react';
import type { ApiStatus } from '@automatizar/shared';

type Connection = 'checking' | 'online' | 'offline';

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking');
  const [checkedAt, setCheckedAt] = useState<string>('—');
  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error('API indisponível');
        const data: ApiStatus = await response.json();
        if (active) { setConnection(data.status === 'ok' ? 'online' : 'offline'); setCheckedAt(new Date(data.timestamp).toLocaleTimeString('pt-BR')); }
      } catch { if (active) setConnection('offline'); }
    };
    void check();
    const timer = window.setInterval(() => void check(), 30_000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);

  return <div className="shell">
    <aside className="sidebar">
      <a className="brand" href="/"><span className="brand-icon"><Zap size={22} fill="currentColor" /></span><span>AUTOMATIZAR<span className="brand-dash">-</span><small>CONTROL CENTER</small></span></a>
      <div className="nav-heading">WORKSPACE</div>
      <nav aria-label="Navegação"><a className="nav-active" href="/"><Layers3 size={18}/> Visão geral</a><span className="nav-disabled"><Bot size={18}/> Automações <small>EM BREVE</small></span><span className="nav-disabled"><Clock3 size={18}/> Histórico <small>EM BREVE</small></span></nav>
      <div className="sidebar-bottom"><div className="avatar">A</div><div><strong>Ambiente local</strong><small>Versão 0.1.0</small></div><CircleCheck size={17} className="bottom-check" /></div>
    </aside>
    <main className="content">
      <header className="topbar"><span><span className="crumb">Workspace</span><span className="slash">/</span> Visão geral</span><span className="environment"><span/> DESENVOLVIMENTO</span></header>
      <section className="hero"><div className="hero-glow"/><div className="eyebrow"><span className="eyebrow-line"/> SEU CENTRO DE OPERAÇÕES</div><h1>Automação começa<br/><em>com uma base sólida.</em></h1><p>A estrutura está pronta. Acompanhe os serviços e prepare as próximas integrações em um só lugar.</p><div className="hero-meta"><span><span className="pulse"/> SISTEMA INICIADO</span><span className="hero-separator"/> MONOREPO · 4 WORKSPACES</div><div className="hero-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="art-core"><Zap size={52} fill="currentColor" /></div><i className="orbit-dot dot-one"/><i className="orbit-dot dot-two"/></div></section>
      <div className="section-title"><div><span className="eyebrow">STATUS DO SISTEMA</span><h2>Seus serviços</h2></div><span className="last-check">Última verificação: {checkedAt}</span></div>
      <div className="cards"><article className="card"><div className="card-top"><span className="card-icon purple"><Activity size={22}/></span><ArrowUpRight size={19} className="card-arrow"/></div><div className="card-label">SERVIÇO DE API</div><h3>Backend</h3><p>Servidor Express e rotas de diagnóstico.</p><div className={`status status-${connection}`}><span/>{connection === 'online' ? 'Online' : connection === 'checking' ? 'Verificando...' : 'Offline'}</div></article><article className="card"><div className="card-top"><span className="card-icon blue"><Bot size={22}/></span><ArrowUpRight size={19} className="card-arrow"/></div><div className="card-label">MOTOR DE EXECUÇÃO</div><h3>Worker</h3><p>Estrutura preparada para receber tarefas.</p><div className="status status-pending"><span/> Aguardando fila</div></article><article className="card"><div className="card-top"><span className="card-icon green"><ShieldCheck size={22}/></span><ArrowUpRight size={19} className="card-arrow"/></div><div className="card-label">ACESSO E SEGURANÇA</div><h3>Autenticação</h3><p>Estrutura reservada para a próxima etapa.</p><div className="status status-pending"><span/> Em preparação</div></article></div>
      <div className="next"><div className="next-icon"><Zap size={20}/></div><div><strong>Próxima etapa: conectar as automações</strong><p>Integraremos a fila, autenticação e credenciais com segurança quando a API externa estiver definida.</p></div><span>ETAPA 02 →</span></div>
      <footer>AUTOMATIZAR- <span>·</span> Estrutura inicial v0.1.0</footer>
    </main>
  </div>;
}
