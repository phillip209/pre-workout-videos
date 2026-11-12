"""Word timing from a finished narration file (no transcription service needed).

Detects pauses in the audio, aligns punctuation boundaries of the known script to those pauses
with a monotonic dynamic-programming match, then spreads words inside each phrase by their
length. Accurate to the phrase; within a phrase it is a proportional estimate. Good enough for
subtitle chunks and animation cues; use ElevenLabs timestamps when available for word accuracy.
"""
from __future__ import annotations

import re

import numpy as np

from . import SR


def detect_pauses(x: np.ndarray, thresh_db=-34.0, min_len=0.07, hop_s=0.01):
    hop = int(hop_s * SR)
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(rms + 1e-9) - 20 * np.log10(rms.max() + 1e-9)
    sil = db < thresh_db
    voiced = np.where(~sil)[0]
    s0, s1 = (voiced[0] * hop_s, (voiced[-1] + 1) * hop_s) if len(voiced) else (0.0, n * hop_s)
    out, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            a, b = i * hop_s, j * hop_s
            if b - a >= min_len and a > s0 and b < s1:
                out.append((a, b))
            i = j
        else:
            i += 1
    return out, s0, s1


def _strength(tok: str) -> int:
    if tok.endswith(("...", "…")):
        return 2
    if tok.endswith((".", "?", "!")):
        return 3
    if tok.endswith((":", ";")):
        return 2
    if tok.endswith(","):
        return 1
    return 0


def align(lines: list[tuple[str, str]], x: np.ndarray):
    """lines = [(line_id, text)]. Returns (words, (s0, s1), pauses, anchors).

    Segmental DP: each punctuation boundary is either matched to a detected pause or left
    unmatched; the cost compares each phrase's real duration with its expected duration
    (global speaking rate x word lengths), so errors don't accumulate along the file.
    """
    words = []
    for lid, text in lines:
        for tok in text.split():
            words.append((tok, lid))
    W = len(words)
    weight = np.array([len(re.sub(r"[^\wáéíóúñü]", "", w.lower())) + 1.5 for w, _ in words], float)
    strength = [_strength(w) for w, _ in words]
    strength[-1] = 0
    pauses, s0, s1 = detect_pauses(x)
    cand = [i for i in range(W) if strength[i] > 0]
    # nodes: 0 = start, 1..K = boundaries, K+1 = end ; pause index -1 = start, J = end
    K, J = len(cand), len(pauses)
    cw = np.concatenate([[0.0], np.cumsum(weight)])  # cumulative weight
    total_pause = sum(b - a for a, b in pauses)
    rate = ((s1 - s0) - total_pause * 0.8) / weight.sum()  # sec per weight unit (approx)
    def p_end(j):
        return s0 if j < 0 else pauses[j][1]
    def p_start(j):
        return s1 if j >= J else pauses[j][0]
    def widx(k):  # last word index of phrase ending at node k
        return cand[k - 1] if 1 <= k <= K else W - 1
    skip_b = {1: 0.25, 2: 0.8, 3: 1.4}
    INF = 1e18
    # dp over (k node, j pause) with k in 0..K+1, j in -1..J
    dp = {(0, -1): 0.0}
    back = {}
    nodes = list(range(1, K + 2))
    for k in nodes:
        jr = range(0, J) if k <= K else [J]
        for j in jr:
            best, arg = INF, None
            for (pk, pj), c in list(dp.items()):
                if pk >= k or pj >= j:
                    continue
                a = (cw[widx(pk) + 1] if pk > 0 else 0.0)
                b = cw[widx(k) + 1]
                exp = max(0.05, (b - a) * rate)
                act = p_start(j) - p_end(pj)
                if act <= 0.05:
                    continue
                inner_pause = sum(pauses[q][1] - pauses[q][0] for q in range(pj + 1, j))
                speech = act - inner_pause * 0.8
                cost = 6.0 * np.log(max(0.05, speech) / exp) ** 2
                cost += sum(skip_b[strength[cand[q - 1]]] for q in range(pk + 1, k) if q <= K)
                cost += sum(0.15 + 1.5 * (pauses[q][1] - pauses[q][0]) for q in range(pj + 1, j))
                if k <= K:
                    cost -= 0.4 * strength[cand[k - 1]] * min(0.6, pauses[j][1] - pauses[j][0])
                if c + cost < best:
                    best, arg = c + cost, (pk, pj)
            if arg is not None:
                dp[(k, j)] = best
                back[(k, j)] = arg
    node = (K + 1, J)
    anchors = {}
    while node != (0, -1):
        k, j = node
        if 1 <= k <= K:
            anchors[cand[k - 1]] = pauses[j]
        node = back[node]
    out = []
    seg_start = s0
    first = 0
    for end_idx in sorted(anchors) + [W - 1]:
        seg_end = anchors[end_idx][0] if end_idx in anchors else s1
        idx = list(range(first, end_idx + 1))
        # unmatched commas inside the segment get a small share of time as a gap
        gaps = [0.10 if (strength[i] > 0 and i != end_idx) else 0.0 for i in idx]
        wsum = sum(weight[i] for i in idx) * rate + sum(gaps)
        span = max(0.05, seg_end - seg_start)
        k_ = span / wsum
        t = seg_start
        for i, g in zip(idx, gaps):
            dur = weight[i] * rate * k_
            out.append((words[i][0], t, t + dur, words[i][1]))
            t += dur + g * k_
        if end_idx in anchors:
            seg_start = anchors[end_idx][1]
        first = end_idx + 1
    return out, (s0, s1), pauses, anchors
