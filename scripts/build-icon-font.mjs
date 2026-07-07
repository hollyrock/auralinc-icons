#!/usr/bin/env node
/**
 * Generate an icon font from prepared SVGs in src/icons/.
 *
 * Expects src/icons/*.svg to already be normalized (64x64) and converted to
 * filled path outlines. Icon glyph names match SVG filenames without .svg.
 */

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { generateFonts } from "fantasticon";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const iconsDir = path.join(repoRoot, "src", "icons");
const distDir = path.join(repoRoot, "dist");

const FONT_NAME = "auralinc-icons";

async function countIcons() {
  const entries = await fs.readdir(iconsDir);
  const svgFiles = entries.filter((name) => name.endsWith(".svg"));

  if (svgFiles.length === 0) {
    throw new Error(`No SVG files found in ${iconsDir}`);
  }

  return svgFiles.length;
}

async function buildFont() {
  await fs.mkdir(distDir, { recursive: true });

  await generateFonts({
    name: FONT_NAME,
    inputDir: iconsDir,
    outputDir: distDir,
    fontTypes: ["woff2", "woff", "ttf"],
    assetTypes: ["css", "json", "html"],
    tag: "i",
    prefix: "icon",
    fontsUrl: "./",
  });
}

async function main() {
  const count = await countIcons();
  await buildFont();
  console.log(`generated icon font for ${count} icon(s) in ${distDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
