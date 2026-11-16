"""Renders the collected results as a self-contained HTML report."""
from __future__ import annotations

import html


CSS = """
:root{--bg:#f6f4f1;--card:#fff;--ink:#1d1a17;--muted:#6b645d;--ok:#1f8a4c;--bad:#c6322a;--skip:#b7791f;--line:#e4dfd8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:32px 20px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:36px 0 12px}.sub{color:var(--muted);margin:0 0 24px}
.status{display:inline-block;padding:6px 14px;border-radius:999px;font-weight:700;color:#fff;margin-bottom:20px}
.status.ok{background:var(--ok)}.status.bad{background:var(--bad)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.tile b{display:block;font-size:26px}.tile span{color:var(--muted);font-size:13px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;font-size:14px}th{background:#faf8f5;color:var(--muted);font-weight:600}
tr:last-child td{border-bottom:0}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;color:#fff}
.pill.passed{background:var(--ok)}.pill.failed{background:var(--bad)}.pill.skipped{background:var(--skip)}
.defect{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--bad);border-radius:12px;padding:16px 18px;margin-bottom:16px}
.defect h3{margin:0 0 6px;font-size:16px}.defect .meta{color:var(--muted);font-size:13px;margin-bottom:8px}
pre{background:#f1eee9;border-radius:8px;padding:10px 12px;overflow:auto;font-size:12.5px;white-space:pre-wrap;word-break:break-word}
.shots{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}.shots a{display:block;max-width:320px}.shots img{width:100%;border:1px solid var(--line);border-radius:8px}
.notes{color:var(--muted);font-size:13px}
@media(max-width:640px){th:nth-child(4),td:nth-child(4){display:none}}
"""


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _screenshots(paths: list[str]) -> str:
    if not paths:
        return ""
    items = "".join(
        f'<a href="{_esc(p)}" target="_blank"><img src="{_esc(p)}" alt="{_esc(p)}" loading="lazy"></a>'
        for p in paths
    )
    return f'<div class="shots">{items}</div>'


def _defect_block(r: dict) -> str:
    extra = ""
    if r["console_errors"]:
        extra += "<p><b>Console errors</b></p><pre>" + _esc("\n".join(r["console_errors"])) + "</pre>"
    if r["failed_requests"]:
        extra += "<p><b>Failed requests</b></p><pre>" + _esc("\n".join(r["failed_requests"])) + "</pre>"
    notes = f'<p class="notes">{_esc("; ".join(r["notes"]))}</p>' if r["notes"] else ""
    return (
        f'<div class="defect"><h3>{_esc(r["name"])}</h3>'
        f'<div class="meta">{_esc(r["category"])} · {_esc(r["module"])} · {r["duration"]:.1f}s</div>'
        f"<pre>{_esc(r['message'])}</pre>{extra}{notes}{_screenshots(r['screenshots'])}</div>"
    )


def _row(r: dict) -> str:
    notes = "; ".join(r["notes"]) if r["notes"] else ""
    if r["outcome"] == "failed" and r["message"]:
        notes = r["message"].strip().splitlines()[0][:160]
    return (
        f"<tr><td><span class=\"pill {r['outcome']}\">{r['outcome']}</span></td>"
        f"<td>{_esc(r['name'])}</td><td>{_esc(r['category'])}</td>"
        f"<td>{r['duration']:.1f}s</td><td class=\"notes\">{_esc(notes)}</td></tr>"
    )


def render_html(data: dict) -> str:
    s = data["summary"]
    defects = [r for r in data["results"] if r["outcome"] == "failed"]
    status_cls = "bad" if defects else "ok"
    status_text = f"{len(defects)} defect(s) found" if defects else "No defects found"
    defects_html = "".join(_defect_block(r) for r in defects) or "<p>No defects were found in this run.</p>"
    rows = "".join(_row(r) for r in data["results"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QA report — {_esc(data['site'])}</title><style>{CSS}</style></head>
<body><main>
<h1>Website QA report</h1>
<p class="sub">Site: <a href="{_esc(data['site'])}">{_esc(data['site'])}</a> · generated {_esc(data['generated_at'])} · {_esc(data['platform'])}</p>
<span class="status {status_cls}">{status_text}</span>
<div class="tiles">
<div class="tile"><b>{s['total']}</b><span>tests</span></div>
<div class="tile"><b style="color:var(--ok)">{s['passed']}</b><span>passed</span></div>
<div class="tile"><b style="color:var(--bad)">{s['failed']}</b><span>failed</span></div>
<div class="tile"><b style="color:var(--skip)">{s['skipped']}</b><span>skipped</span></div>
<div class="tile"><b>{data['duration_seconds']}s</b><span>duration</span></div>
</div>
<h2>Defects</h2>
{defects_html}
<h2>All checks</h2>
<table><thead><tr><th>Result</th><th>Test</th><th>Type</th><th>Time</th><th>Details</th></tr></thead><tbody>{rows}</tbody></table>
</main></body></html>"""
