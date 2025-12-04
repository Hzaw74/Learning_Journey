import { Point } from "./ink-engine";

export type ShapeType = 'rectangle' | 'circle' | 'triangle' | 'line' | 'unknown';

export class ShapeRecognizer {
    static recognize(points: Point[]): { type: ShapeType, path?: string, bounds?: any } | null {
        if (points.length < 10) return null; // Too short

        const start = points[0];
        const end = points[points.length - 1];

        // Check if closed shape (start and end are close)
        const dist = Math.hypot(end.x - start.x, end.y - start.y);
        const isClosed = dist < 20; // Threshold

        // Calculate bounding box
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const p of points) {
            minX = Math.min(minX, p.x);
            minY = Math.min(minY, p.y);
            maxX = Math.max(maxX, p.x);
            maxY = Math.max(maxY, p.y);
        }
        const w = maxX - minX;
        const h = maxY - minY;

        if (isClosed) {
            // Simple heuristic: Check aspect ratio and "fullness"
            // A circle fills ~78% of its bounding box area (pi*r^2 / 4r^2 = pi/4)
            // A rect fills 100%
            // A triangle fills 50%

            // Note: This is very rudimentary. A real implementation would use $1 recognizer or similar.

            // For now, let's just return a Rectangle for closed shapes as a placeholder
            // or try to differentiate Circle vs Rect.

            // Let's assume it's a rectangle for now if it's roughly boxy
            return {
                type: 'rectangle',
                path: `M ${minX} ${minY} L ${maxX} ${minY} L ${maxX} ${maxY} L ${minX} ${maxY} Z`,
                bounds: { x: minX, y: minY, w, h }
            };
        } else {
            // Check if it's a line
            // If all points are close to the line segment start-end
            return {
                type: 'line',
                path: `M ${start.x} ${start.y} L ${end.x} ${end.y}`,
                bounds: { x: Math.min(start.x, end.x), y: Math.min(start.y, end.y), w: Math.abs(end.x - start.x), h: Math.abs(end.y - start.y) }
            };
        }
    }
}
