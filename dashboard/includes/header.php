<?php
/** Shared HTML head + nav for the dashboard. */
?><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windsurf Quota Dashboard</title>
    <link rel="stylesheet" href="/dashboard/assets/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js" defer></script>
</head>
<body>
<header class="topbar">
    <h1>Windsurf Quota</h1>
    <div class="meta">Updated: <span id="last-updated"><?= wq_e(wq_format_ts($latest['timestamp'] ?? null)) ?></span></div>
</header>
<main class="container">
