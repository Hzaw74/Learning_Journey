import { createWorker } from 'tesseract.js';
import { InkEngine, Point } from './ink-engine';

export class OCRService {
    static async recognizeStrokes(strokes: { points: Point[] }[]): Promise<string> {
        if (strokes.length === 0) return "";

        // 1. Determine bounds
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const stroke of strokes) {
            for (const p of stroke.points) {
                minX = Math.min(minX, p.x);
                minY = Math.min(minY, p.y);
                maxX = Math.max(maxX, p.x);
                maxY = Math.max(maxY, p.y);
            }
        }

        // Add padding
        const padding = 20;
        minX -= padding;
        minY -= padding;
        maxX += padding;
        maxY += padding;
        const width = maxX - minX;
        const height = maxY - minY;

        // 2. Create off-screen canvas
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (!ctx) return "";

        // Fill white background (Tesseract likes high contrast)
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, width, height);

        // 3. Render strokes
        ctx.translate(-minX, -minY);
        ctx.fillStyle = "black";
        for (const stroke of strokes) {
            const pathStr = InkEngine.getStrokePath(stroke.points);
            const p = new Path2D(pathStr);
            ctx.fill(p);
        }

        // 4. Convert to image
        const dataUrl = canvas.toDataURL('image/png');

        // 5. Run Tesseract
        const worker = await createWorker('eng');
        const ret = await worker.recognize(dataUrl);
        await worker.terminate();

        return ret.data.text.trim();
    }
}
