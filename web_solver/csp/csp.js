#!/usr/bin/env node

var csp = require('./csp_evaluator');

var rawCsp = "default-src 'self' https://*.google.com https://*.googleapis.com https://*.twitter.com; connect-src 'none'; font-src 'none'; frame-src 'none'; img-src 'self'; manifest-src 'none'; media-src 'none'; object-src 'none'; style-src 'self'; worker-src 'none'; frame-ancestors 'none'; block-all-mixed-content;";
var parser = new csp.CspParser(rawCsp);
var evaluator = new csp.CspEvaluator(parser.csp, csp.Version.CSP3);
var findings = evaluator.evaluate();
console.log(findings);