from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


def _sparkline(values: List[float]) -> str:
    """Generate a simple SVG sparkline."""
    if not values:
        return ""
    points = [f"{i * 25},{40 - v}" for i, v in enumerate(values)]
    return (
        '<svg width="100" height="40" viewBox="0 0 100 40" class="sparkline">'
        f'<polyline points="{' '.join(points)}"/>'
        '</svg>'
    )


def generate_dashboard_html(data: Dict[str, Any]) -> str:
    """Generate HTML dashboard from data dictionary."""
    kpi_html = []
    for name, vals in data["kpis"].items():
        delta = ((vals["actual"] - vals["w1"]) / vals["w1"] * 100) if vals["w1"] else 0
        trend = [vals.get("w3", 0), vals.get("w2", 0), vals.get("w1", 0), vals["actual"]]
        card = f"""
        <div class='kpi-card'>
            <h3>{name.upper()}</h3>
            <p class='value'>{vals['actual']}</p>
            <p class='delta'>{delta:.2f}% vs w-1</p>
            {_sparkline(trend)}
        </div>
        """
        kpi_html.append(card)

    funnel = data["funnel"]
    funnel_steps = list(funnel.items())
    max_val = funnel_steps[0][1]
    funnel_html = []
    drops = []
    for i, (label, val) in enumerate(funnel_steps):
        pct = val / max_val * 100 if max_val else 0
        if i > 0:
            prev = funnel_steps[i-1][1]
            rate = val / prev * 100 if prev else 0
            drops.append((rate, label))
        funnel_html.append(
            f"<div class='bar'><span>{label}</span><div class='bar-bg'><div class='bar-fill' style='width:{pct:.2f}%'></div></div><span>{val}</span></div>"
        )
    biggest_drop = min(drops)[1] if drops else ""

    publicos_rows = []
    for p in data.get("publicos", []):
        publicos_rows.append(
            f"<tr><td>{p['nombre']}</td><td><div class='bar-cell' style='--w:{p['gasto']}px'>{p['gasto']}</div></td>"
            f"<td><div class='bar-cell' style='--w:{p['compras']}px'>{p['compras']}</div></td>"
            f"<td class='heat' data-val='{p['roas']}'>{p['roas']}</td>"
            f"<td class='heat' data-val='{p['cpa']}'>{p['cpa']}</td>"
            f"<td>{p['ctr']}</td><td>{p['freq']}</td></tr>"
        )

    ads_cards = []
    for ad in data.get("ads_top", []):
        thumb = f"<img src='{ad['thumb']}' alt='thumb'/>" if ad.get('thumb') else ""
        ads_cards.append(
            f"<div class='ad-card'>{thumb}<h4>{ad['nombre']}</h4><p>ROAS {ad['roas']}</p><p>Compras {ad['compras']}</p></div>"
        )

    acciones = ''.join(f"<li>{a}</li>" for a in data.get("acciones", []))

    creatividad = data.get("creatividad", {})
    ctr_vals = [creatividad.get("ctr_link", {}).get(k, 0) for k in ("w3", "w2", "w1", "actual")]
    hook_vals = [creatividad.get("hook_rate", {}).get(k, 0) for k in ("w3", "w2", "w1", "actual")]
    tiempo = creatividad.get("tiempo_video_s", {}).get("actual", 0)
    creatividad_html = f"""
    <div class='creatividad'>
      <div class='mini'>{_sparkline(ctr_vals)}{_sparkline(hook_vals)}<p>CTR / Hook</p></div>
      <div class='mini'><div class='bar-bg'><div class='bar-fill' style='width:{tiempo}px'></div></div><p>Tiempo medio video</p></div>
    </div>
    """

    html = f"""
<!DOCTYPE html>
<html lang='es'>
<head>
<meta charset='utf-8'/>
<title>Reporte</title>
<style>
body {{font-family: 'Exo 2', sans-serif; background:#111827; color:#e5e7eb; margin:16px;}}
header {{display:flex; justify-content:space-between; align-items:center;}}
.kpi-stack {{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:16px;}}
.kpi-card {{background:#1F2937; padding:16px; border-radius:12px;}}
.bar {{display:flex; align-items:center; gap:8px; margin:4px 0;}}
.bar-bg {{flex:1; background:#1F2937; border-radius:12px;}}
.bar-fill {{background:#18579B; height:16px; border-radius:12px;}}
.table {{width:100%; border-collapse:collapse;}}
.table td, .table th {{padding:8px;}}
.bar-cell {{position:relative; background:#1F2937; border-radius:12px; padding:4px;}}
.bar-cell::after {{content:''; position:absolute; top:0; left:0; height:100%; width:var(--w); background:#18579B; border-radius:12px; z-index:-1;}}
.heat[data-val] {{background:linear-gradient(90deg,#EF4444,var(--color,#22C55E));}}
.ad-gallery {{display:flex; gap:12px; flex-wrap:wrap;}}
.ad-card {{background:#1F2937; padding:12px; border-radius:12px; width:200px;}}
.actions {{background:#1F2937; padding:16px; border-radius:12px;}}
.sparkline polyline {{fill:none; stroke:#22C55E; stroke-width:2;}}
.creatividad {{display:flex; gap:16px;}}
.mini {{background:#1F2937; padding:12px; border-radius:12px; flex:1; text-align:center;}}
</style>
</head>
<body>
<header><h1>Reporte: {data['rango']['inicio']} – {data['rango']['fin']}</h1></header>
<section class='kpi-stack'>{''.join(kpi_html)}</section>
<section>
  <h2>Embudo</h2>
  {''.join(funnel_html)}
  <p>Mayor drop: {biggest_drop}</p>
</section>
<section>
  <h2>Creatividad & Tracción</h2>
  {creatividad_html}
</section>
<section>
  <h2>Públicos / Ad Sets</h2>
  <table class='table'>
  <tr><th>Nombre</th><th>Gasto</th><th>Compras</th><th>ROAS</th><th>CPA</th><th>CTR</th><th>Freq</th></tr>
  {''.join(publicos_rows)}
  </table>
</section>
<section>
  <h2>Top Anuncios</h2>
  <div class='ad-gallery'>{''.join(ads_cards)}</div>
</section>
<section class='actions'>
  <h2>Acciones recomendadas</h2>
  <ul>{acciones}</ul>
</section>
</body>
</html>
"""
    return html


def save_dashboard(data: Dict[str, Any], output: Path) -> None:
    output.write_text(generate_dashboard_html(data), encoding='utf-8')


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def load_excel(path: Path) -> Dict[str, Any]:
    import pandas as pd
    return json.loads(Path(path).read_text())  # placeholder

