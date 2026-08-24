# -*- coding: utf-8 -*-
"""通过 Crossref 查询论文期刊，并对照分区库判断是否为一区。"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZONES_PATH = ROOT / "journal_zones.json"

_CACHE: dict[str, dict] = {}
_ZONES_DATA: dict | None = None

# 云边协同计算（CECC）判定：对齐《云边协同计算领域文献综述》三维分类体系
_CECC_CORE = (
    r"cloud[\s\-–—]?edge",
    r"edge[\s\-–—]?cloud",
    r"cloudedge",
    r"edgecloud",
    r"cloud[\s\-–—]?edge[\s\-–—]?(end|terminal)",
    r"end[\s\-–—]?edge[\s\-–—]?cloud",
    r"edge[\s\-–—]?hub[\s\-–—]?cloud",
    r"edge[\s\-–—]?cloud[\s\-–—]?continuum",
    r"cloud[\s\-–—]?edge[\s\-–—]?(collabor|cooper)",
    r"edge[\s\-–—]?cloud[\s\-–—]?(collabor|cooper)",
    r"edge[\s\-–—]?collabor",
    r"mobile[\s\-–—]?cloud[\s\-–—]?edge",
    r"serverless[\s\-–—]?edge",
    r"云边协同",
    r"云边协作",
    r"云边计算",
    r"云边",
    r"边云",
)
_CECC_EDGE = (
    r"mobile[\s\-–—]?edge[\s\-–—]?comput",
    r"multi[\s\-–—]?access[\s\-–—]?edge",
    r"\bmec\b",
    r"edge[\s\-–—]?comput",
    r"vehicular[\s\-–—]?edge",
    r"uav[\s\-–—]?(based[\s\-–—]?)?edge",
    r"edge[\s\-–—]?server",
    r"edge[\s\-–—]?node",
    r"collaborative[\s\-–—]?edge[\s\-–—]?comput",
    r"serverless[\s\-–—]?edge",
    r"federated[\s\-–—]?edge[\s\-–—]?learn",
    r"edge[\s\-–—]?orchestrat",
    r"edge[\s\-–—]?shard",
    r"edge[\s\-–—]?collabor",
    r"dynamic[\s\-–—]?edge[\s\-–—]?network",
    r"\bon[\s\-–—]?edge\b",
    r"tasks[\s\-–—]?on[\s\-–—]?edge",
)
_CECC_TASK = (
    r"task[\s\-–—]?offload",
    r"computation[\s\-–—]?offload",
    r"compute[\s\-–—]?offload",
    r"computing[\s\-–—]?offload",
    r"resource[\s\-–—]?alloc",
    r"service[\s\-–—]?(cach|deploy|migr|orchestr|placement|select|routing)",
    r"workflow[\s\-–—]?(schedul|container)",
    r"task[\s\-–—]?(placement|schedul|alloc)",
    r"load[\s\-–—]?balanc",
    r"container",
    r"serverless",
    r"\bsfc\b",
    r"kubernetes|\bk8s\b",
)
_CECC_ZH = (
    r"边缘协作",
    r"边缘计算",
    r"边计算",
    r"边缘编排",
    r"无服务器边",
    r"云边",
    r"边云",
    r"卸载",
    r"调度",
    r"端边云",
    r"边云协同",
    r"云边协同",
)
_CECC_METHOD = (
    r"federated[\s\-–—]?learn",
    r"federated[\s\-–—]?reinforcement",
    r"deep[\s\-–—]?reinforcement",
    r"\bdrl\b",
    r"\bmarl\b",
    r"\bmaddpg\b",
    r"lyapunov",
    r"blockchain",
    r"digital[\s\-–—]?twin",
    r"auction",
    r"game[\s\-–—]?theoret",
    r"stackelberg",
    r"differential[\s\-–—]?privacy",
    r"over[\s\-–—]?the[\s\-–—]?air",
    r"beamform",
    r"client[\s\-–—]?sampl",
)


def _cecc_score(norm: str) -> tuple[int, str]:
    """按综述 taxonomy 计算 CECC 相关度得分。"""
    if not norm:
        return 0, "无有效文本"

    for pat in _CECC_CORE:
        if re.search(pat, norm, re.I):
            return 5, "匹配云边协同核心主题"

    for pat in _CECC_ZH:
        if re.search(pat, norm):
            return 4, "匹配云边协同中文主题"

    score = 0
    reasons: list[str] = []

    has_edge = any(re.search(p, norm, re.I) for p in _CECC_EDGE)
    has_task = any(re.search(p, norm, re.I) for p in _CECC_TASK)
    has_cloud = bool(re.search(r"\bcloud\b", norm, re.I))
    has_method = any(re.search(p, norm, re.I) for p in _CECC_METHOD)
    has_collab = bool(re.search(r"collabor|cooper", norm, re.I))
    has_cloud_assist = bool(re.search(r"cloud[\s\-–—]?assist", norm, re.I))
    has_infer = bool(re.search(r"infer|inference|llm|dnn|deep[\s\-–—]?learn", norm, re.I))
    has_iot = bool(re.search(r"\biot\b|internet[\s\-–—]?of[\s\-–—]?things|iiot|aiot", norm, re.I))

    if has_edge:
        score += 3
        reasons.append("边缘计算场景")
    if has_task:
        score += 2
        reasons.append("卸载/调度/编排")
    if has_cloud and (has_edge or has_collab or has_task):
        score += 3
        reasons.append("云-边联合优化")
    if has_cloud_assist and has_edge:
        score += 3
        reasons.append("云辅助边端计算")
    if has_collab and (has_edge or has_infer or has_cloud):
        score += 2
        reasons.append("多层协作计算/推理")
    if has_infer and has_edge:
        score += 2
        reasons.append("边缘 AI 推理")
    if re.search(r"v2x|vehicular", norm, re.I) and (has_task or has_edge):
        score += 2
        reasons.append("车联网边缘优化")
    if re.search(r"federated[\s\-–—]?learn", norm, re.I) and re.search(
        r"edge|iot|mec|iiot|aiot|aggreg|device|client|communic|privacy|offload|resource|over[\s\-–—]?the[\s\-–—]?air|beamform|sampling",
        norm,
        re.I,
    ):
        score += 2
        reasons.append("云边协同方法学(联邦学习/边缘通信)")
    elif has_method and (has_edge or has_iot or has_task or has_cloud):
        score += 2
        reasons.append("云边协同方法学(优化/DRL/机制等)")
    if re.search(r"satellite", norm, re.I) and has_edge:
        score += 2
        reasons.append("空天地边缘协同")
    if re.search(r"energy|latency|delay|aoi|reliability|trust|privacy|cost|budget", norm, re.I) and (
        has_edge or has_task or has_cloud
    ):
        score += 1
        reasons.append("CECC 典型优化目标")

    detail = " · ".join(reasons[:3]) if reasons else "未识别云边协同计算相关主题"
    return score, detail


def classify_cloud_edge_research(text: str, *, local_corpus: bool = False) -> dict:
    """判断文本是否属于云边协同计算研究方向。"""
    if local_corpus:
        score, detail = _cecc_score(normalize_journal(text.replace("_", " ").replace("-", " ")))
        label_detail = detail if score > 0 else "云边协同精读文献"
        return {
            "is_cecc": True,
            "cecc_label": "是",
            "cecc_detail": f"本地精读库 · {label_detail}",
        }

    norm = normalize_journal(text.replace("_", " ").replace("-", " "))
    score, detail = _cecc_score(norm)
    if score >= 2:
        return {"is_cecc": True, "cecc_label": "是", "cecc_detail": detail}
    return {"is_cecc": False, "cecc_label": "否", "cecc_detail": detail}


def _load_zones() -> dict:
    global _ZONES_DATA
    if _ZONES_DATA is None:
        _ZONES_DATA = json.loads(ZONES_PATH.read_text(encoding="utf-8"))
    return _ZONES_DATA


def normalize_journal(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _match_journal(journal_name: str) -> tuple[str | None, dict | None]:
    data = _load_zones()
    journals = data.get("journals", {})
    aliases = data.get("aliases", {})

    if not journal_name:
        return None, None

    raw = journal_name.strip()
    if raw in aliases:
        raw = aliases[raw]
    if raw in journals:
        return raw, journals[raw]

    norm = normalize_journal(raw)
    for key, info in journals.items():
        if normalize_journal(key) == norm:
            return key, info

    for alias, target in aliases.items():
        if normalize_journal(alias) == norm:
            return target, journals.get(target)

    for key, info in journals.items():
        kn = normalize_journal(key)
        if kn in norm or norm in kn:
            return key, info

    return raw, None


def zone_info_from_journal(journal_name: str) -> dict:
    matched, info = _match_journal(journal_name)
    if info is None:
        return {
            "journal": journal_name or "",
            "matched_journal": matched,
            "cas_zone": None,
            "jcr_quartile": None,
            "is_zone1": None,
            "zone_label": "分区未知",
            "zone_detail": "期刊未收录在本地分区库，可手动核对中科院分区",
        }

    cas_zone = info.get("cas_zone")
    jcr = info.get("jcr_quartile")
    is_zone1 = cas_zone == 1
    if is_zone1:
        label = "中科院一区"
    elif cas_zone is not None:
        label = f"中科院{cas_zone}区"
    else:
        label = "分区未知"

    detail_parts = [f"中科院 {cas_zone} 区" if cas_zone else None, f"JCR {jcr}" if jcr else None]
    return {
        "journal": journal_name,
        "matched_journal": matched,
        "cas_zone": cas_zone,
        "jcr_quartile": jcr,
        "is_zone1": is_zone1,
        "zone_label": label,
        "zone_detail": " · ".join(p for p in detail_parts if p),
    }


def _crossref_search(title: str) -> dict | None:
    query = urllib.parse.quote(title.strip()[:120])
    url = f"https://api.crossref.org/works?query.title={query}&rows=5"
    req = urllib.request.Request(url, headers={"User-Agent": "literature-pdf-lookup/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        items = json.loads(resp.read())["message"]["items"]
    if not items:
        return None

    allowed_types = {"journal-article", "proceedings-article"}
    items = [it for it in items if it.get("type") in allowed_types] or items

    def title_score(item: dict) -> float:
        cr_title = (item.get("title") or [""])[0]
        a = normalize_journal(title)
        b = normalize_journal(cr_title)
        if a == b:
            return 1.0
        if a in b or b in a:
            overlap = min(len(a), len(b)) / max(len(a), len(b))
            return 0.7 + 0.15 * overlap
        aw = set(a.split())
        bw = set(b.split())
        if not aw:
            return 0.0
        word_score = len(aw & bw) / len(aw)
        if len(aw) <= 2 and word_score < 1.0:
            return word_score * 0.5
        return word_score

    best = max(items, key=title_score)
    if title_score(best) < 0.45:
        return None
    container = best.get("container-title") or []
    journal = container[0] if container else ""
    return {
        "crossref_title": (best.get("title") or [""])[0],
        "journal": journal,
        "doi": best.get("DOI", ""),
        "match_score": round(title_score(best), 2),
    }


def lookup_paper_by_title(title: str, use_cache: bool = True) -> dict:
    key = normalize_journal(title)
    if not key:
        return {"query": title, "found": False, "error": "标题为空"}

    if use_cache and key in _CACHE:
        return _CACHE[key]

    result = {
        "query": title,
        "found": False,
        "local": False,
        "crossref_title": "",
        "journal": "",
        "doi": "",
        "match_score": 0,
        "cas_zone": None,
        "jcr_quartile": None,
        "is_zone1": None,
        "zone_label": "未查询",
        "zone_detail": "",
    }

    try:
        cr = _crossref_search(title)
    except Exception as exc:
        result["error"] = f"Crossref 查询失败: {exc}"
        _CACHE[key] = result
        return result

    if not cr:
        result["zone_label"] = "未找到论文"
        result["zone_detail"] = "Crossref 未匹配到该标题，请检查拼写或换用英文全称"
        _CACHE[key] = result
        return result

    zone = zone_info_from_journal(cr["journal"])
    cecc = classify_cloud_edge_research(f"{title} {cr['crossref_title']}")
    result.update(
        {
            "found": True,
            "crossref_title": cr["crossref_title"],
            "journal": cr["journal"],
            "doi": cr["doi"],
            "match_score": cr["match_score"],
            **zone,
            **cecc,
        }
    )
    _CACHE[key] = result
    return result


def enrich_paper_item(item: dict) -> dict:
    """为本地文献条目补充分区信息。"""
    lookup = lookup_paper_by_title(item["title"])
    enriched = dict(item)
    enriched["journal"] = lookup.get("journal") or ""
    enriched["crossref_title"] = lookup.get("crossref_title") or ""
    enriched["cas_zone"] = lookup.get("cas_zone")
    enriched["jcr_quartile"] = lookup.get("jcr_quartile")
    enriched["is_zone1"] = lookup.get("is_zone1")
    enriched["zone_label"] = lookup.get("zone_label") or "分区未知"
    enriched["zone_detail"] = lookup.get("zone_detail") or ""
    enriched["local"] = True
    cecc = classify_cloud_edge_research(
        " ".join(
            filter(
                None,
                [
                    item.get("title"),
                    item.get("filename"),
                    item.get("summary"),
                    lookup.get("crossref_title"),
                ],
            )
        ),
        local_corpus=True,
    )
    enriched.update(cecc)
    return enriched
