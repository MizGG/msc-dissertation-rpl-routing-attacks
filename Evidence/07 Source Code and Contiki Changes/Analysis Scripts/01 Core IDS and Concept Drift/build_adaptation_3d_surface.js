#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const input = path.join('experiments', '90 Raw Reproducibility Workspace', 'cross_attack_adaptation_with_sybil_v1', 'cross_attack_adaptation_summary.csv');
const outDir = path.join('experiments', '90 Raw Reproducibility Workspace', 'dissertation_final_figures_v2');
const outSvg = path.join(outDir, 'adaptation_f1_3d_surface.svg');
const outCsv = path.join(outDir, 'tables', 'adaptation_f1_3d_surface_data.csv');

const familyLabels = {
  blackhole: 'Blackhole',
  dio_suppression: 'DIO suppression',
  dis_flood: 'DIS flood',
  grayhole: 'Grayhole',
  increase_rank: 'Increase rank',
  sinkhole: 'Sinkhole',
  sybil: 'Sybil',
  wormhole: 'Wormhole',
  worst_parent: 'Worst parent',
};
const familyOrder = Object.keys(familyLabels);

function esc(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function colour(value) {
  const stops = [
    [0.00, [44, 123, 182]],
    [0.35, [102, 194, 165]],
    [0.60, [255, 223, 119]],
    [0.80, [244, 109, 67]],
    [1.00, [165, 0, 38]],
  ];
  for (let i = 1; i < stops.length; i++) {
    if (value <= stops[i][0]) {
      const [a, b] = [stops[i - 1], stops[i]];
      const t = (value - a[0]) / (b[0] - a[0]);
      const rgb = a[1].map((n, j) => Math.round(n + (b[1][j] - n) * t));
      return `rgb(${rgb.join(',')})`;
    }
  }
  return 'rgb(165,0,38)';
}
function point(x, y, z) {
  const sx = 760 + (x - y) * 86;
  const sy = 690 + (x + y) * 29 - z * 410;
  return [sx, sy];
}
function polygon(points, fill, opacity = 1) {
  return `<polygon points="${points.map(p => p.join(',')).join(' ')}" fill="${fill}" fill-opacity="${opacity}" stroke="#263238" stroke-width="1.2"/>`;
}

const [header, ...lines] = fs.readFileSync(input, 'utf8').trim().split(/\r?\n/);
const columns = header.split(',');
const index = Object.fromEntries(columns.map((name, i) => [name, i]));
const aggregate = new Map();
for (const line of lines) {
  const row = line.split(',');
  const source = row[index.source_family];
  const target = row[index.target_family];
  const seedCount = Number(row[index.adaptation_seed_count]);
  const f1 = Number(row[index.mean_f1]);
  if (source === target || !familyLabels[target]) continue;
  const key = `${target}|${seedCount}`;
  const record = aggregate.get(key) || { target, seedCount, sum: 0, count: 0 };
  record.sum += f1;
  record.count += 1;
  aggregate.set(key, record);
}
const data = [];
for (const target of familyOrder) {
  for (let seedCount = 0; seedCount <= 3; seedCount++) {
    const record = aggregate.get(`${target}|${seedCount}`);
    if (!record) throw new Error(`Missing data for ${target}, ${seedCount}`);
    data.push({ target, seedCount, meanF1: record.sum / record.count, sourceFamilies: record.count });
  }
}
fs.mkdirSync(path.dirname(outCsv), { recursive: true });
fs.writeFileSync(outCsv, ['target_family,adaptation_seed_count,mean_held_out_f1,source_families_averaged', ...data.map(d => `${d.target},${d.seedCount},${d.meanF1.toFixed(6)},${d.sourceFamilies}`)].join('\n') + '\n');

const valueAt = (familyIndex, seedCount) => data.find(d => d.target === familyOrder[familyIndex] && d.seedCount === seedCount).meanF1;
let svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100">\n`;
svg += `<rect width="1600" height="1100" fill="#ffffff"/>\n`;
svg += `<text x="800" y="72" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="700" fill="#12212b">Held-Out F1 by Adaptation Budget and Target Attack Family</text>\n`;
svg += `<text x="800" y="110" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="19" fill="#455a64">Mean across eight source-family CART models; target-family axis is categorical</text>\n`;

const base = [point(0, 0, 0), point(3, 0, 0), point(3, 8, 0), point(0, 8, 0)];
svg += polygon(base, '#f2f5f6');
for (let x = 0; x <= 3; x++) {
  const a = point(x, 0, 0), b = point(x, 8, 0);
  svg += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#b0bec5" stroke-width="1"/>`;
}
for (let y = 0; y <= 8; y++) {
  const a = point(0, y, 0), b = point(3, y, 0);
  svg += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#b0bec5" stroke-width="1"/>`;
}
for (const z of [0.25, 0.5, 0.75, 1]) {
  const a = point(0, 8, z), b = point(3, 8, z);
  svg += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#cfd8dc" stroke-width="1" stroke-dasharray="5 5"/>`;
  svg += `<text x="${a[0] - 47}" y="${a[1] + 6}" text-anchor="end" font-family="Arial" font-size="16" fill="#37474f">${z.toFixed(2)}</text>`;
}
for (let y = 0; y < 8; y++) {
  for (let x = 0; x < 3; x++) {
    const z00 = valueAt(y, x), z10 = valueAt(y, x + 1), z01 = valueAt(y + 1, x), z11 = valueAt(y + 1, x + 1);
    const p00 = point(x, y, z00), p10 = point(x + 1, y, z10), p11 = point(x + 1, y + 1, z11), p01 = point(x, y + 1, z01);
    svg += polygon([p00, p10, p11], colour((z00 + z10 + z11) / 3), 0.96);
    svg += polygon([p00, p11, p01], colour((z00 + z11 + z01) / 3), 0.96);
  }
}
const [origin, xEnd, yEnd, zEnd] = [point(0, 0, 0), point(3, 0, 0), point(0, 8, 0), point(0, 0, 1)];
for (const end of [xEnd, yEnd, zEnd]) svg += `<line x1="${origin[0]}" y1="${origin[1]}" x2="${end[0]}" y2="${end[1]}" stroke="#12212b" stroke-width="2.5"/>`;
for (let x = 0; x <= 3; x++) {
  const p = point(x, 0, 0);
  svg += `<text x="${p[0]}" y="${p[1] + 30}" text-anchor="middle" font-family="Arial" font-size="18" fill="#12212b">${x}</text>`;
}
for (let y = 0; y < familyOrder.length; y++) {
  const p = point(0, y, 0);
  svg += `<text x="${p[0] - 22}" y="${p[1] + 5}" text-anchor="end" font-family="Arial" font-size="16" fill="#12212b">${esc(familyLabels[familyOrder[y]])}</text>`;
}
svg += `<text x="1030" y="800" text-anchor="middle" transform="rotate(19 1030 800)" font-family="Arial" font-size="22" font-weight="700" fill="#12212b">Target seeds used for adaptation</text>`;
svg += `<text x="265" y="500" text-anchor="middle" transform="rotate(-19 265 500)" font-family="Arial" font-size="22" font-weight="700" fill="#12212b">Target attack family</text>`;
svg += `<text x="180" y="315" text-anchor="middle" transform="rotate(-90 180 315)" font-family="Arial" font-size="22" font-weight="700" fill="#12212b">Mean held-out F1</text>`;
svg += `<text x="795" y="960" text-anchor="middle" font-family="Arial" font-size="18" fill="#455a64">Each point averages results from eight source-family models. Surfaces connect discrete family categories for visual comparison only.</text>`;
const cbX = 1370, cbY = 265, cbH = 340;
for (let i = 0; i < 100; i++) {
  const v = i / 99;
  svg += `<rect x="${cbX}" y="${cbY + cbH - (i + 1) * cbH / 100}" width="30" height="${cbH / 100 + 1}" fill="${colour(v)}"/>`;
}
svg += `<rect x="${cbX}" y="${cbY}" width="30" height="${cbH}" fill="none" stroke="#263238" stroke-width="1"/>`;
svg += `<text x="1385" y="235" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700" fill="#12212b">F1</text>`;
for (const v of [0, 0.25, 0.5, 0.75, 1]) {
  const y = cbY + cbH - v * cbH;
  svg += `<line x1="1400" y1="${y}" x2="1408" y2="${y}" stroke="#263238" stroke-width="1"/>`;
  svg += `<text x="1415" y="${y + 5}" font-family="Arial" font-size="16" fill="#263238">${v.toFixed(2)}</text>`;
}
svg += `</svg>\n`;
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(outSvg, svg);
console.log(`Wrote ${outSvg}`);
console.log(`Wrote ${outCsv}`);
