<?php

declare(strict_types=1);

use PhpCsFixer\Config;
use PhpCsFixer\Finder;

$finder = Finder::create()
    ->files()
    ->in(__DIR__ . '/docs')
    ->name('*.php');

return (new Config())
    ->setRiskyAllowed(false)
    ->setFinder($finder);
