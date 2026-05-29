#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db.py — Capa de datos PMO · Nine Fitness Brescia 19
Backend 1 (nube):  GitHub JSON API  →  datos persistentes en el repo
Backend 2 (local): SQLite           →  fallback sin configuración
"""

import json
import sqlite3
import urllib.request
import urllib.error
import base64
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import streamlit as st

# ─── RUTAS JSON EN EL REPO GITHUB ────────────────────────────────
_GH_PATH_DIARIAS   = "actas_data/actas_diarias.json"
_GH_PATH_SEMANALES = "actas_data/actas_semanales.json"
_GH_PATH_REGISTRO  = "actas_data/registro_actas.json"

# ─── DETECCIÓN DE BACKEND ────────────────────────────────────────

def _backend() -> str:
    try:
        if "github" in st.secrets and st.secrets["github"].get("token","").startswith("ghp_"):
            return "github"
    except Exception:
        pass
    return "sqlite"

# ─── GITHUB API ──────────────────────────────────────────────────

def _gh_headers() -> dict:
    token = st.secrets["github"]["token"]
    return {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
        "User-Agent":    "pmo-brescia19",
    }

@st.cache_data(ttl=30, show_spinner=False)
def _gh_read(path: str) -> tuple:
    """(data: list, sha: str) — cacheado 30 s."""
    repo = st.secrets["github"]["repo"]
    url  = f"https://api.github.com/repos/{repo}/contents/{path}"
    req  = urllib.request.Request(url, headers=_gh_headers())
    try:
        resp    = json.loads(urllib.request.urlopen(req, timeout=10).read())
        content = json.loads(base64.b64decode(resp["content"]).decode("utf-8"))
        return content, resp["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return [], ""
        raise

def _gh_write(path: str, data: list, sha: str, msg: str = "PMO update"):
    """Commit al repo con los datos serializados."""
    repo  = st.secrets["github"]["repo"]
    url   = f"https://api.github.com/repos/{repo}/contents/{path}"
    body  = {
        "message": msg,
        "content": base64.b64encode(
            json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        ).decode("ascii"),
    }
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="PUT",
        headers={**_gh_headers(), "Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=15)
    _gh_read.clear()   # invalida caché

def _gh_upsert(path: str, new_record: dict):
    """Lee lista, inserta/actualiza por id, escribe de vuelta."""
    data, sha = _gh_read(path)
    data = [r for r in data if r.get("id") != new_record["id"]]
    data.append(new_record)
    data.sort(key=lambda x: x.get("fecha",""), reverse=True)
    _gh_write(path, data, sha, f"PMO upsert {new_record['id']}")

def _gh_delete(path: str, record_id: str):
    data, sha = _gh_read(path)
    data = [r for r in data if r.get("id") != record_id]
    _gh_write(path, data, sha, f"PMO delete {record_id}")

# ─── SQLITE ───────────────────────────────────────────────────────

def _sqlite():
    p = Path("actas_data/pmo_brescia19.db")
    p.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(p), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

_JSON_FIELDS = [
    "intervenciones", "definiciones_tecnicas", "agenda_proxima",
    "incidencias", "gremios_incidencia", "desviaciones_criticas", "hitos_cumplidos",
    "acuerdos_tecnicos", "galeria_imagenes",
]

def _to_dict(row) -> dict:
    d = dict(row)
    for f in _JSON_FIELDS:
        if f in d and isinstance(d[f], str) and d[f]:
            try:
                d[f] = json.loads(d[f])
            except Exception:
                pass
    return d

def _to_sql(rec: dict) -> dict:
    out = dict(rec)
    for f in _JSON_FIELDS:
        if f in out and not isinstance(out[f], str):
            out[f] = json.dumps(out[f], ensure_ascii=False)
    return out

# ─── INIT ─────────────────────────────────────────────────────────

def init_db():
    if _backend() == "sqlite":
        conn = _sqlite()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS actas_diarias (
            id                    TEXT PRIMARY KEY,
            fecha                 TEXT NOT NULL,
            semana_obra           INTEGER,
            obra                  TEXT DEFAULT 'Brescia 19',
            fase                  TEXT,
            intervenciones        TEXT,
            definiciones_tecnicas TEXT,
            agenda_proxima        TEXT,
            incidencias           TEXT,
            gremios_incidencia    TEXT,
            prioridad             TEXT DEFAULT 'normal',
            estado                TEXT DEFAULT 'borrador',
            texto_original        TEXT,
            resumen               TEXT,
            creado_por            TEXT DEFAULT 'Dario A. Lopez',
            created_at            TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_ad_fecha ON actas_diarias(fecha);

        CREATE TABLE IF NOT EXISTS actas_semanales (
            id                    TEXT PRIMARY KEY,
            semana_obra           INTEGER,
            semana_ano            TEXT,
            fecha_inicio          TEXT,
            fecha_fin             TEXT,
            obra                  TEXT DEFAULT 'Brescia 19',
            resumen_ejecutivo     TEXT,
            desviaciones_criticas TEXT,
            hitos_cumplidos       TEXT,
            actas_diarias_ids     TEXT,
            estado_aprobacion     TEXT DEFAULT 'borrador',
            aprobado_por          TEXT,
            created_at            TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS registro_actas (
            id                    TEXT PRIMARY KEY,
            fecha                 TEXT NOT NULL,
            obra                  TEXT DEFAULT 'Brescia 19',
            semana_obra           INTEGER,
            fase                  TEXT,
            redactor              TEXT DEFAULT 'Dario A. Lopez',
            estado_general        TEXT DEFAULT 'en_curso',
            resumen_ejecutivo     TEXT,
            intervenciones        TEXT,
            definiciones_tecnicas TEXT,
            acuerdos_tecnicos     TEXT,
            agenda_proxima        TEXT,
            incidencias           TEXT,
            galeria_imagenes      TEXT,
            created_at            TEXT DEFAULT (datetime('now')),
            updated_at            TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_ra_fecha ON registro_actas(fecha);
        """)
        conn.commit()
        # Migrar actas_diarias.json si la tabla está vacía
        jf = Path("actas_data/actas_diarias.json")
        if jf.exists():
            existing = {r[0] for r in conn.execute("SELECT id FROM actas_diarias")}
            for rec in json.loads(jf.read_text(encoding="utf-8")):
                if rec["id"] not in existing:
                    s = _to_sql(rec)
                    conn.execute(
                        f"INSERT OR IGNORE INTO actas_diarias ({','.join(s)}) VALUES ({','.join(['?']*len(s))})",
                        list(s.values()),
                    )
            conn.commit()

def semana_obra(d: date) -> int:
    return max(1, (d - date(2026, 3, 23)).days // 7 + 1)

def backend_info() -> str:
    b = _backend()
    if b == "github":
        repo = st.secrets["github"]["repo"]
        return f"☁️ GitHub · {repo}"
    return "💾 SQLite local"

# ══════════════════════════════════════════════════════════════════
#  CRUD — ACTAS DIARIAS
# ══════════════════════════════════════════════════════════════════

def list_actas_diarias(
    desde: str = "2026-01-01",
    hasta: str = "2026-12-31",
    prioridad: str = "todas",
    estado: str = "todos",
) -> list[dict]:
    if _backend() == "github":
        data, _ = _gh_read(_GH_PATH_DIARIAS)
        result = [
            r for r in data
            if desde <= r.get("fecha","") <= hasta
            and (prioridad == "todas" or r.get("prioridad") == prioridad)
            and (estado    == "todos"  or r.get("estado")    == estado)
        ]
        return sorted(result, key=lambda x: x.get("fecha",""), reverse=True)
    else:
        sql  = "SELECT * FROM actas_diarias WHERE fecha>=? AND fecha<=?"
        p    = [desde, hasta]
        if prioridad != "todas": sql += " AND prioridad=?"; p.append(prioridad)
        if estado    != "todos":  sql += " AND estado=?";    p.append(estado)
        sql += " ORDER BY fecha DESC"
        return [_to_dict(r) for r in _sqlite().execute(sql, p).fetchall()]


def upsert_acta_diaria(rec: dict):
    if _backend() == "github":
        _gh_upsert(_GH_PATH_DIARIAS, rec)
    else:
        conn = _sqlite()
        s = _to_sql(rec)
        conn.execute(
            f"INSERT OR REPLACE INTO actas_diarias ({','.join(s)}) VALUES ({','.join(['?']*len(s))})",
            list(s.values()),
        )
        conn.commit()


def get_acta_diaria(rec_id: str) -> Optional[dict]:
    if _backend() == "github":
        data, _ = _gh_read(_GH_PATH_DIARIAS)
        return next((r for r in data if r.get("id") == rec_id), None)
    else:
        row = _sqlite().execute("SELECT * FROM actas_diarias WHERE id=?", [rec_id]).fetchone()
        return _to_dict(row) if row else None


def delete_acta_diaria(rec_id: str):
    if _backend() == "github":
        _gh_delete(_GH_PATH_DIARIAS, rec_id)
    else:
        conn = _sqlite(); conn.execute("DELETE FROM actas_diarias WHERE id=?", [rec_id]); conn.commit()


# ══════════════════════════════════════════════════════════════════
#  CRUD — ACTAS SEMANALES
# ══════════════════════════════════════════════════════════════════

def list_actas_semanales() -> list[dict]:
    if _backend() == "github":
        data, _ = _gh_read(_GH_PATH_SEMANALES)
        return sorted(data, key=lambda x: x.get("fecha_inicio",""), reverse=True)
    else:
        return [_to_dict(r) for r in _sqlite().execute(
            "SELECT * FROM actas_semanales ORDER BY fecha_inicio DESC"
        ).fetchall()]


def upsert_acta_semanal(rec: dict):
    if _backend() == "github":
        _gh_upsert(_GH_PATH_SEMANALES, rec)
    else:
        conn = _sqlite(); s = _to_sql(rec)
        conn.execute(
            f"INSERT OR REPLACE INTO actas_semanales ({','.join(s)}) VALUES ({','.join(['?']*len(s))})",
            list(s.values()),
        )
        conn.commit()


def delete_acta_semanal(rec_id: str):
    if _backend() == "github":
        _gh_delete(_GH_PATH_SEMANALES, rec_id)
    else:
        conn = _sqlite(); conn.execute("DELETE FROM actas_semanales WHERE id=?", [rec_id]); conn.commit()


# ══════════════════════════════════════════════════════════════════
#  CONSOLIDACIÓN SEMANAL
# ══════════════════════════════════════════════════════════════════

_DIAS_ES_DB  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
_MESES_ES_DB = ["enero","febrero","marzo","abril","mayo","junio","julio",
                "agosto","septiembre","octubre","noviembre","diciembre"]

def _parse_list_field(val) -> list:
    """Devuelve siempre una lista, parseando JSON string si hace falta."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            r = json.loads(val)
            return r if isinstance(r, list) else [r]
        except Exception:
            return []
    return []

def consolidar_semana(semana: int) -> dict:
    lunes   = date(2026, 3, 23) + timedelta(weeks=semana - 1)
    viernes = lunes + timedelta(days=6)
    diarias = list_actas_diarias(lunes.isoformat(), viernes.isoformat())
    if not diarias:
        return {}

    # gremios_incidencia puede ser JSON string — parsear antes de iterar
    gremios_inc = sorted({
        g for a in diarias
        for g in _parse_list_field(a.get("gremios_incidencia"))
    })

    # logros y solicitudes agregados de todas las diarias
    hitos = []
    for a in diarias:
        for l in _parse_list_field(a.get("logros_tecnicos")):
            if isinstance(l, dict) and l.get("descripcion"):
                hitos.append(l["descripcion"])

    # Resumen ejecutivo con fechas en español
    def _dia_es(fecha_str):
        try:
            d = datetime.fromisoformat(fecha_str)
            return f"{_DIAS_ES_DB[d.weekday()][:3]} {d.day:02d}/{d.month:02d}"
        except Exception:
            return fecha_str

    resumen = "\n".join(
        f"• {_dia_es(a['fecha'])}: {a.get('resumen','')}"
        for a in diarias
    )

    return {
        "id":                    f"SEM-{semana:02d}-{lunes.year}",
        "semana_obra":           semana,
        "semana_ano":            f"S{semana:02d}/{lunes.year}",
        "fecha_inicio":          lunes.isoformat(),
        "fecha_fin":             viernes.isoformat(),
        "obra":                  "Brescia 19",
        "resumen_ejecutivo":     resumen,
        "desviaciones_criticas": gremios_inc,
        "hitos_cumplidos":       hitos,
        "actas_diarias_ids":     ",".join(a["id"] for a in diarias),
        "estado_aprobacion":     "borrador",
        "aprobado_por":          "Darío A. López",
    }


# ══════════════════════════════════════════════════════════════════
#  CRUD — REGISTRO ACTAS (documentos oficiales)
# ══════════════════════════════════════════════════════════════════

def list_registro_actas(desde: str = "2026-01-01", hasta: str = "2026-12-31") -> list[dict]:
    if _backend() == "github":
        data, _ = _gh_read(_GH_PATH_REGISTRO)
        result = [r for r in data if desde <= r.get("fecha", "") <= hasta]
        return sorted(result, key=lambda x: x.get("fecha", ""), reverse=True)
    else:
        rows = _sqlite().execute(
            "SELECT * FROM registro_actas WHERE fecha>=? AND fecha<=? ORDER BY fecha DESC",
            [desde, hasta],
        ).fetchall()
        return [_to_dict(r) for r in rows]


def get_registro_acta(rec_id: str) -> Optional[dict]:
    if _backend() == "github":
        data, _ = _gh_read(_GH_PATH_REGISTRO)
        return next((r for r in data if r.get("id") == rec_id), None)
    else:
        row = _sqlite().execute(
            "SELECT * FROM registro_actas WHERE id=?", [rec_id]
        ).fetchone()
        return _to_dict(row) if row else None


def upsert_registro_acta(rec: dict):
    rec["updated_at"] = datetime.now().isoformat()
    if _backend() == "github":
        _gh_upsert(_GH_PATH_REGISTRO, rec)
    else:
        conn = _sqlite()
        s = _to_sql(rec)
        conn.execute(
            f"INSERT OR REPLACE INTO registro_actas ({','.join(s)}) VALUES ({','.join(['?']*len(s))})",
            list(s.values()),
        )
        conn.commit()


def delete_registro_acta(rec_id: str):
    if _backend() == "github":
        _gh_delete(_GH_PATH_REGISTRO, rec_id)
    else:
        conn = _sqlite()
        conn.execute("DELETE FROM registro_actas WHERE id=?", [rec_id])
        conn.commit()
