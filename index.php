<?php
/**
 * Entry point for the PHP dashboard.
 * Laragon auto-vhost serves this at http://windsurf_api.test/
 * (assuming the project folder is reachable from C:\laragon\www\windsurf_api,
 *  e.g. via symlink: mklink /D C:\laragon\www\windsurf_api I:\CodeProjects\windsurf_api)
 */
require __DIR__ . '/dashboard/views/home.php';
