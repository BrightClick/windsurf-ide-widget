<?php
/**
 * Generic helpers: parse percent strings, format timestamps, classify quota state.
 */

/**
 * Extract numeric percentage from a string like "85.3% remaining".
 */
function wq_parse_percent(?string $s): ?float {
    if (!$s) return null;
    if (preg_match('/([\d.]+)\s*%/', $s, $m)) {
        return (float)$m[1];
    }
    return null;
}

/**
 * Color class (green/yellow/red) based on remaining percent.
 */
function wq_pct_class(?float $pct): string {
    if ($pct === null) return 'unknown';
    if ($pct >= 50) return 'ok';
    if ($pct >= 20) return 'warn';
    return 'crit';
}

/**
 * Convert ISO timestamp to a human-friendly local representation.
 */
function wq_format_ts(?string $iso): string {
    if (!$iso) return '—';
    try {
        $dt = new DateTime($iso);
        return $dt->format('Y-m-d H:i:s');
    } catch (Exception $e) {
        return $iso;
    }
}

/**
 * Escape for HTML output.
 */
function wq_e($v): string {
    return htmlspecialchars((string)($v ?? ''), ENT_QUOTES, 'UTF-8');
}
