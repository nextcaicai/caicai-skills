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
