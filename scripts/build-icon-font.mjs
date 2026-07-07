#!/usr/bin/env node
/**
 * Convert stroked SVGs to filled paths and generate an icon font.
 *
 * Reads src/icons/*.svg, outlines strokes in place, then writes font assets to dist/.
 * Icon glyph names match SVG filenames without the .svg extension.
 */

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { generateFonts } from "fantasticon";

const require = createRequire(import.meta.url);
const outlineStroke = require("svg-outline-stroke");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const iconsDir = path.join(repoRoot, "src", "icons");
const distDir = path.join(repoRoot, "dist");

const FONT_NAME = "auralinc-icons";

async function outlineIcons() {
  const entries = await fs.readdir(iconsDir);
  const svgFiles = entries.filter((name) => name.endsWith(".svg")).sort();

  if (svgFiles.length === 0) {
    throw new Error(`No SVG files found in ${iconsDir}`);
  }

  for (const fileName of svgFiles) {
    const filePath = path.join(iconsDir, fileName);
    const source = await fs.readFile(filePath, "utf8");
    const outlined = await outlineStroke(source, { color: "#000000" });
    await fs.writeFile(filePath, outlined, "utf8");
    console.log(`outlined ${fileName}`);
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
  const count = await outlineIcons();
  await buildFont();
  console.log(`generated icon font for ${count} icon(s) in ${distDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
