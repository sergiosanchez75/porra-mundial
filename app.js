/* Porra Mundial 2026 */
document.addEventListener('DOMContentLoaded', init);

function init() {
  // Timestamp
  const ts = DATOS.ultimaActualizacion;
  document.getElementById('ultima-actualizacion').textContent = ts
    ? '🟢 Actualizado: ' + new Date(ts).toLocaleString('es-ES')
    : '⚪ Sin resultados todavía — ejecuta actualizar.py para sincronizar con la API';

  // Header stats
  const jugados = Object.keys(DATOS.resultados).length;
  const total   = DATOS.partidos.length;
  const np      = DATOS.pronosticos.participantes.length;
  document.getElementById('stat-part').textContent     = np;
  document.getElementById('stat-partidos').textContent = jugados + '/' + total;

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
  });

  renderClasificacion();
  renderPartidos();
  renderSelectPersona();
}

/* ── Motor de puntuación ──────────────────────────────────────────────── */
function signo(gl, gv) { return gl > gv ? 'L' : gl < gv ? 'V' : 'E'; }

function calcularPuntos() {
  const pts = {};
  DATOS.pronosticos.participantes.forEach(p => { pts[p] = { signos: 0, exactos: 0, total: 0 }; });

  DATOS.partidos.forEach(partido => {
    const r = DATOS.resultados[partido.id];
    if (!r) return;
    const sr = signo(r.gl, r.gv);

    DATOS.pronosticos.participantes.forEach(persona => {
      const a = (DATOS.pronosticos.apuestas[persona] || {})[partido.id];
      if (!a) return;
      if (signo(a.gl, a.gv) === sr) {
        pts[persona].signos++;
        pts[persona].total++;
        if (a.gl === r.gl && a.gv === r.gv) { pts[persona].exactos++; pts[persona].total++; }
      }
    });
  });
  return pts;
}

/* ── Clasificación ────────────────────────────────────────────────────── */
function renderClasificacion() {
  const pts = calcularPuntos();
  const personas = [...DATOS.pronosticos.participantes]
    .sort((a, b) => (pts[b].total || 0) - (pts[a].total || 0));

  if (personas.length === 0) {
    document.getElementById('podium').innerHTML =
      '<div style="grid-column:1/-1"><div class="empty"><span class="empty-icon">📋</span><span>Sin pronósticos cargados</span></div></div>';
    return;
  }

  const maxPts = pts[personas[0]].total || 1;

  // Podium (top 3 visual: 2nd | 1st | 3rd)
  const podiumEl  = document.getElementById('podium');
  const medals    = ['🥇','🥈','🥉'];
  const posClass  = ['pos-1','pos-2','pos-3'];
  const podiumOrd = [1, 0, 2]; // display order: silver | gold | bronze

  podiumEl.innerHTML = '';
  podiumOrd.forEach(idx => {
    const persona = personas[idx];
    const card = document.createElement('div');
    if (!persona) { card.className = 'podium-card'; card.style.visibility = 'hidden'; podiumEl.appendChild(card); return; }
    const p = pts[persona];
    card.className = 'podium-card ' + posClass[idx];
    card.innerHTML =
      '<div class="podium-stripe"></div>' +
      '<div class="podium-medal">' + medals[idx] + '</div>' +
      '<div class="podium-avatar">' + persona.charAt(0).toUpperCase() + '</div>' +
      '<div class="podium-name">' + persona + '</div>' +
      '<div class="podium-pts">' + p.total + '</div>' +
      '<div class="podium-sub">✓ ' + p.signos + ' &nbsp;·&nbsp; 🎯 ' + p.exactos + '</div>';
    podiumEl.appendChild(card);
  });

  // Full ranking
  const body = document.getElementById('ranking-body');
  body.innerHTML = '';
  personas.forEach((persona, idx) => {
    const p   = pts[persona];
    const pct = Math.round((p.total / maxPts) * 100);
    const row = document.createElement('div');
    row.className = 'ranking-row';
    row.innerHTML =
      '<div class="rank-num">' + (idx + 1) + '</div>' +
      '<div class="rank-name-cell">' +
        '<div class="rank-avatar">' + persona.charAt(0).toUpperCase() + '</div>' +
        '<span>' + persona + '</span>' +
      '</div>' +
      '<div class="rank-pts-cell col-center">' + p.signos + '</div>' +
      '<div class="rank-pts-cell col-center">' + p.exactos + '</div>' +
      '<div class="rank-total-cell col-right">' +
        '<span class="pts-big">' + p.total + '</span>' +
        '<div class="pts-bar"><div class="pts-bar-fill" style="width:' + pct + '%"></div></div>' +
      '</div>';
    body.appendChild(row);
  });
}

/* ── Partidos ─────────────────────────────────────────────────────────── */
function renderPartidos() {
  const grupos = ['todos','A','B','C','D','E','F','G','H','I','J','K','L'];
  const cont = document.getElementById('filtros-grupo');
  grupos.forEach(g => {
    const btn = document.createElement('button');
    btn.className = 'grupo-btn' + (g === 'todos' ? ' active' : '');
    btn.dataset.grupo = g;
    btn.textContent = g === 'todos' ? 'Todos' : 'Grupo ' + g;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.grupo-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      mostrarPartidos(g);
    });
    cont.appendChild(btn);
  });
  mostrarPartidos('todos');
}

function mostrarPartidos(grupo) {
  const lista = document.getElementById('lista-partidos');
  lista.innerHTML = '';
  const hoy = new Date().toISOString().slice(0, 10);

  const partidos = grupo === 'todos'
    ? DATOS.partidos
    : DATOS.partidos.filter(p => p.grupo === grupo);

  const porFecha = {};
  partidos.forEach(p => { (porFecha[p.fecha] = porFecha[p.fecha] || []).push(p); });

  Object.keys(porFecha).sort().forEach(fecha => {
    const hdr = document.createElement('div');
    hdr.className = 'fecha-hdr';
    hdr.textContent = formatFecha(fecha);
    lista.appendChild(hdr);

    porFecha[fecha].forEach(partido => {
      const r     = DATOS.resultados[partido.id];
      const esHoy = fecha === hoy;
      const estado = r ? 'jugado' : esHoy ? 'hoy' : 'pendiente';

      // Accuracy
      let signos = 0, exactos = 0;
      const np = DATOS.pronosticos.participantes.length;
      if (r && np > 0) {
        const sr = signo(r.gl, r.gv);
        DATOS.pronosticos.participantes.forEach(persona => {
          const a = (DATOS.pronosticos.apuestas[persona] || {})[partido.id];
          if (!a) return;
          if (signo(a.gl, a.gv) === sr) { signos++; if (a.gl === r.gl && a.gv === r.gv) exactos++; }
        });
      }

      const scoreHTML = r
        ? '<div class="score-wrap jugado"><div class="score-nums">' + r.gl + ' · ' + r.gv + '</div></div>'
        : '<div class="score-wrap"><div class="score-vs">VS</div></div>';

      let pillsHTML = '';
      if (r && np > 0) {
        pillsHTML =
          '<div class="pills">' +
          '<span class="pill pill-green">✓ ' + signos + '/' + np + '</span>' +
          '<span class="pill pill-gold">🎯 ' + exactos + '/' + np + '</span>' +
          '</div>';
      } else if (esHoy && !r) {
        pillsHTML = '<span class="pill pill-live">EN JUEGO HOY</span>';
      }

      const card = document.createElement('div');
      card.className = 'match-card ' + estado;
      card.innerHTML =
        '<div class="match-card-accent"></div>' +
        '<div class="match-inner">' +
          '<div class="match-meta">' +
            '<span class="grupo-badge g-' + partido.grupo + '">Grupo ' + partido.grupo + '</span>' +
            '<span class="match-hora">' + partido.hora + ' · ' + partido.sede + '</span>' +
          '</div>' +
          '<div class="match-teams">' +
            '<div class="team-local">'  + partido.local     + '</div>' +
            scoreHTML +
            '<div class="team-visit">' + partido.visitante + '</div>' +
          '</div>' +
          '<div class="match-footer">' +
            '<button class="btn-info" title="Ver pronósticos">ⓘ</button>' +
            pillsHTML +
          '</div>' +
        '</div>';
      card.querySelector('.btn-info').addEventListener('click', () => abrirModalPartido(partido.id));
      lista.appendChild(card);
    });
  });
}

/* ── Detalle ──────────────────────────────────────────────────────────── */
function renderSelectPersona() {
  const sel = document.getElementById('persona-select');
  DATOS.pronosticos.participantes.forEach(p => {
    const o = document.createElement('option');
    o.value = p; o.textContent = p;
    sel.appendChild(o);
  });
  sel.addEventListener('change', () => renderDetallePersona(sel.value));
}

function renderDetallePersona(persona) {
  const div = document.getElementById('detalle-persona');
  div.innerHTML = '';
  if (!persona) return;

  const pts = calcularPuntos();
  const p   = pts[persona] || { signos: 0, exactos: 0, total: 0 };

  // Header card
  const hcard = document.createElement('div');
  hcard.className = 'persona-header-card';
  hcard.innerHTML =
    '<div class="persona-avatar-lg">' + persona.charAt(0).toUpperCase() + '</div>' +
    '<div>' +
      '<div class="persona-name">' + persona + '</div>' +
      '<div class="persona-chips">' +
        '<div class="pchip c-total"><strong>' + p.total + '</strong><span>Total pts</span></div>' +
        '<div class="pchip"><strong>' + p.signos + '</strong><span>Signos ✓</span></div>' +
        '<div class="pchip c-exacto"><strong>' + p.exactos + '</strong><span>Exactos 🎯</span></div>' +
      '</div>' +
    '</div>';
  div.appendChild(hcard);

  // Tabla
  const tabla = document.createElement('div');
  tabla.className = 'detalle-card';
  tabla.innerHTML =
    '<div class="drow dhdr">' +
      '<div>Partido</div>' +
      '<div style="text-align:center">Pronóstico</div>' +
      '<div style="text-align:center">Resultado</div>' +
      '<div style="text-align:center">Pts</div>' +
    '</div>';

  DATOS.partidos.forEach(partido => {
    const a = (DATOS.pronosticos.apuestas[persona] || {})[partido.id];
    const r = DATOS.resultados[partido.id];

    let clase = 'pend', ptsStr = '⏳';
    if (r && a) {
      const ok = signo(a.gl, a.gv) === signo(r.gl, r.gv);
      if (ok && a.gl === r.gl && a.gv === r.gv) { clase = 'exacto'; ptsStr = '🎯 +2'; }
      else if (ok) { clase = 'signo'; ptsStr = '+1'; }
      else         { clase = 'fallo'; ptsStr = '0'; }
    } else if (r && !a) { clase = 'fallo'; ptsStr = '—'; }

    const row = document.createElement('div');
    row.className = 'drow ' + clase;
    row.innerHTML =
      '<div>' + partido.local + ' vs ' + partido.visitante + '</div>' +
      '<div class="dc">' + (a ? a.gl + '-' + a.gv : '—') + '</div>' +
      '<div class="dc">' + (r ? r.gl + '-' + r.gv : '⏳') + '</div>' +
      '<div class="dp">' + ptsStr + '</div>';
    tabla.appendChild(row);
  });

  div.appendChild(tabla);
}

/* ── Modal pronósticos ────────────────────────────────────────────────── */
function abrirModalPartido(id) {
  const partido = DATOS.partidos.find(p => p.id === id);
  if (!partido) return;
  const r = DATOS.resultados[id];

  document.getElementById('modal-titulo').textContent =
    partido.local + '  ·  ' + partido.visitante;

  const body = document.getElementById('modal-body');
  body.innerHTML =
    '<div class="modal-row mhdr">' +
      '<div>Participante</div>' +
      '<div style="text-align:center">Pronóstico</div>' +
      '<div style="text-align:center">Resultado</div>' +
      '<div style="text-align:center">Pts</div>' +
    '</div>';

  DATOS.pronosticos.participantes.forEach(persona => {
    const a = (DATOS.pronosticos.apuestas[persona] || {})[id];
    let clase = 'm-pend', ptsStr = '⏳';

    if (r && a) {
      const ok = signo(a.gl, a.gv) === signo(r.gl, r.gv);
      if (ok && a.gl === r.gl && a.gv === r.gv) { clase = 'm-exacto'; ptsStr = '🎯 +2'; }
      else if (ok)                               { clase = 'm-signo';  ptsStr = '+1'; }
      else                                       { clase = 'm-fallo';  ptsStr = '0'; }
    } else if (r && !a) { clase = 'm-fallo'; ptsStr = '—'; }

    const row = document.createElement('div');
    row.className = 'modal-row ' + clase;
    row.innerHTML =
      '<div class="modal-persona">' +
        '<div class="modal-avatar">' + persona.charAt(0).toUpperCase() + '</div>' +
        persona +
      '</div>' +
      '<div class="mc">' + (a ? a.gl + '-' + a.gv : '—') + '</div>' +
      '<div class="mc">' + (r ? r.gl + '-' + r.gv : '⏳') + '</div>' +
      '<div class="mp">' + ptsStr + '</div>';
    body.appendChild(row);
  });

  document.getElementById('modal-overlay').classList.add('open');
}

function cerrarModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

/* ── Util ─────────────────────────────────────────────────────────────── */
function formatFecha(str) {
  return new Date(str + 'T12:00:00').toLocaleDateString('es-ES',
    { weekday: 'long', day: 'numeric', month: 'long' });
}
