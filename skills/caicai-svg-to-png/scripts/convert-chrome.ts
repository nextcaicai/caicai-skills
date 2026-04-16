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
