---
name: caicai-svg-to-png
description: Convert SVG files to PNG. Use this skill when the user wants to convert SVG to PNG. If the user mentions Chrome extension, browser extension, manifest.json icons, or specifically asks for Chrome plugin icon sizes, convert to FOUR PNG files (16x16, 32x32, 48x48, 128x128). If the user simply says "svg to png", "convert svg to png", or only mentions converting/format conversion without specifying Chrome/extension context, convert to a SINGLE PNG file. This skill uses TypeScript and Sharp for fast, high-quality image conversion.
---

# SVG to PNG Converter

Convert SVG files to PNG format. Supports two modes based on user intent detection.

## Mode Detection

Analyze the user's request to determine which mode to use:

### Mode A: Chrome Extension Icons (4 files)
**Trigger phrases:**
- "Chrome extension icons"
- "browser extension icons"
- "manifest.json icons"
- "Chrome plugin icon"
- "icon16.png", "icon32.png", "icon48.png", "icon128.png"
- "Chrome 扩展图标"
- "插件图标"
- "manifest 图标"

**Output:**
- `{svg-name}/icon16.png` (16x16) - toolbar icon
- `{svg-name}/icon32.png` (32x32) - Windows/Mac retina
- `{svg-name}/icon48.png` (48x48) - Chrome Web Store listing
- `{svg-name}/icon128.png` (128x128) - Chrome Web Store main

### Mode B: Single PNG (1 file)
**Trigger phrases:**
- "svg to png"
- "convert svg to png"
- "svg 转 png"
- "svg 转换 png"
- "导出 png"
- "format conversion" without extension context

**Output:**
- `{svg-name}/{svg-name}.png` - Single PNG file (default 512x512, or user-specified size)

## Output Directory Structure

All PNG files are organized in a folder named after the SVG file (without extension):

```
project-root/
├── reading.svg
├── reading/                    ← 自动创建的文件夹
│   ├── icon16.png             ← Chrome 扩展模式
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
│
├── logo.svg
├── logo/                       ← 自动创建的文件夹
│   └── logo.png               ← 单张模式 (默认 512x512)
│
└── favicon.svg
└── favicon/                    ← 自动创建的文件夹
    └── favicon.png            ← 单张模式 (例如 32x32)
```

## Prerequisites Check

Before proceeding, verify:
- Node.js installed
- npm or yarn available
- Sharp library installed: `npm install sharp @types/sharp typescript --save-dev`

If Sharp is missing, install it before proceeding.

## Workflow

1. **Detect user intent** - Analyze the request for Chrome/extension keywords
2. **Ask for clarification if needed** - If unclear, ask: "Do you need Chrome extension icons (4 sizes) or a single PNG?"
3. **Get SVG file path** - Ask if not provided
4. **For single PNG mode:** Ask for desired output size (default 512x512)
5. **Run the appropriate conversion** - PNG 会保存到以 SVG 命名的文件夹中
6. **Report results** - 显示完整的文件夹路径和文件列表

## Scripts

### Script 1: Chrome Extension Icons (convert-chrome.ts)

```typescript
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

const CHROME_ICON_SIZES = [16, 32, 48, 128];

async function svgToChromeIcons(svgPath: string): Promise<void> {
    const resolvedPath = path.resolve(svgPath);

    if (!fs.existsSync(resolvedPath)) {
        console.error(`Error: File '${svgPath}' not found`);
        process.exit(1);
    }

    // 以 SVG 文件名（不含扩展名）创建输出目录
    const svgName = path.basename(resolvedPath, '.svg');
    const outputDir = path.join(process.cwd(), svgName);
    
    // 确保目录存在
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log(`Converting ${path.basename(svgPath)} to Chrome extension icons...`);
    console.log(`Output directory: ${outputDir}/\n`);

    const svgBuffer = fs.readFileSync(resolvedPath);

    for (const size of CHROME_ICON_SIZES) {
        const outputFile = path.join(outputDir, `icon${size}.png`);

        await sharp(svgBuffer)
            .resize(size, size, {
                fit: 'contain',
                background: { r: 0, g: 0, b: 0, alpha: 0 }
            })
            .png({ compressionLevel: 9, effort: 10 })
            .toFile(outputFile);

        console.log(`  ✓ Generated: ${svgName}/icon${size}.png (${size}x${size})`);
    }

    console.log(`\nDone! Icons saved to: ${outputDir}/`);
    console.log(`Files: ${CHROME_ICON_SIZES.map(s => `icon${s}.png`).join(', ')}`);
}

const svgPath = process.argv[2] || 'icon.svg';
svgToChromeIcons(svgPath).catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
```

### Script 2: Single PNG (convert-single.ts)

```typescript
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

async function svgToPng(svgPath: string, size?: number): Promise<void> {
    const resolvedPath = path.resolve(svgPath);

    if (!fs.existsSync(resolvedPath)) {
        console.error(`Error: File '${svgPath}' not found`);
        process.exit(1);
    }

    // 以 SVG 文件名（不含扩展名）创建输出目录
    const svgName = path.basename(resolvedPath, '.svg');
    const outputDir = path.join(process.cwd(), svgName);
    const outputSize = size || 512;
    const outputFile = path.join(outputDir, `${svgName}.png`);
    
    // 确保目录存在
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log(`Converting ${path.basename(svgPath)} to PNG (${outputSize}x${outputSize})...`);
    console.log(`Output directory: ${outputDir}/\n`);

    const svgBuffer = fs.readFileSync(resolvedPath);

    await sharp(svgBuffer)
        .resize(outputSize, outputSize, {
            fit: 'contain',
            background: { r: 0, g: 0, b: 0, alpha: 0 }
        })
        .png({ compressionLevel: 9, effort: 10 })
        .toFile(outputFile);

    console.log(`\nDone! Saved: ${svgName}/${svgName}.png (${outputSize}x${outputSize})`);
}

const svgPath = process.argv[2] || 'icon.svg';
const size = process.argv[3] ? parseInt(process.argv[3]) : undefined;

svgToPng(svgPath, size).catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
```

## Running the Conversion

### Chrome Extension Mode

```bash
npx tsc scripts/convert-chrome.ts --esModuleInterop --module commonjs --target es2020
node scripts/convert-chrome.js <path-to-svg>
```

**Example:**
```bash
node scripts/convert-chrome.js reading.svg
# Creates: reading/icon16.png, reading/icon32.png, reading/icon48.png, reading/icon128.png
```

### Single PNG Mode

```bash
npx tsc scripts/convert-single.ts --esModuleInterop --module commonjs --target es2020
# Default 512x512:
node scripts/convert-single.js <path-to-svg>
# Custom size:
node scripts/convert-single.js <path-to-svg> <size>
```

**Example:**
```bash
node scripts/convert-single.js logo.svg 256
# Creates: logo/logo.png (256x256)
```

## Example Interactions

### Example 1: Chrome Extension
**User:** "Convert reading.svg to Chrome extension icons"

**Action:**
1. Copy `scripts/convert-chrome.ts` to project
2. Run: `npx tsc convert-chrome.ts && node convert-chrome.js reading.svg`
3. Report: "Created folder 'reading/' with icon16.png, icon32.png, icon48.png, icon128.png"

### Example 2: Single PNG
**User:** "svg to png"

**Action:**
1. Ask: "Which SVG file?"
2. Ask: "What size? (default 512x512)"
3. Copy `scripts/convert-single.ts` to project
4. Run: `npx tsc convert-single.ts && node convert-single.js logo.svg 256`
5. Report: "Created folder 'logo/' with logo.png (256x256)"

### Example 3: Ambiguous
**User:** "Convert icon.svg"

**Action:**
Ask: "Do you need Chrome extension icons (4 sizes) or a single PNG?"

## Error Handling

- If SVG file doesn't exist → Report clearly
- If Sharp not installed → Provide `npm install` command
- If TypeScript compilation fails → Show error, suggest Node.js version check
- If folder creation fails → Report permission issue

## manifest.json Reference (Chrome Extension Mode)

```json
{
  "icons": {
    "16": "reading/icon16.png",
    "32": "reading/icon32.png",
    "48": "reading/icon48.png",
    "128": "reading/icon128.png"
  }
}
```
