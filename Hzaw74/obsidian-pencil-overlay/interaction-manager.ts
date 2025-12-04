import { Point } from "./ink-engine";

export interface DrawableObject {
    id: string;
    type: 'stroke' | 'image';
    points?: Point[]; // For strokes
    path?: string;    // SVG path data
    bounds: { x: number, y: number, w: number, h: number };
    x: number;
    y: number;
    color?: string;
}

export class InteractionManager {
    selectedObjects: DrawableObject[] = []; // Multiple selection
    selectedObject: DrawableObject | null = null; // Primary selection (keep for compat)
    isDragging = false;
    dragStart: Point | null = null;
    objectStartPos: Map<string, { x: number, y: number }> = new Map();

    hitTest(objects: DrawableObject[], point: Point): DrawableObject | null {
        // Simple bounding box hit test
        // Iterate in reverse to select top-most object
        for (let i = objects.length - 1; i >= 0; i--) {
            const obj = objects[i];
            if (point.x >= obj.bounds.x && point.x <= obj.bounds.x + obj.bounds.w &&
                point.y >= obj.bounds.y && point.y <= obj.bounds.y + obj.bounds.h) {
                return obj;
            }
        }
        return null;
    }

    selectInPolygon(objects: DrawableObject[], polygon: Point[]) {
        this.selectedObjects = [];
        this.selectedObject = null;

        // Simple bounding box check first, then point-in-polygon if needed
        // For this MVP, let's just check if object center is inside polygon

        for (const obj of objects) {
            const cx = obj.bounds.x + obj.bounds.w / 2;
            const cy = obj.bounds.y + obj.bounds.h / 2;

            if (this.isPointInPolygon({ x: cx, y: cy, p: 0 }, polygon)) {
                this.selectedObjects.push(obj);
            }
        }

        if (this.selectedObjects.length > 0) {
            this.selectedObject = this.selectedObjects[0];
        }
    }

    isPointInPolygon(point: Point, polygon: Point[]): boolean {
        let inside = false;
        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const xi = polygon[i].x, yi = polygon[i].y;
            const xj = polygon[j].x, yj = polygon[j].y;

            const intersect = ((yi > point.y) !== (yj > point.y))
                && (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    }

    startDrag(object: DrawableObject, point: Point) {
        this.selectedObject = object;
        this.selectedObjects = [object]; // Reset multi-selection on single click
        this.isDragging = true;
        this.dragStart = point;
        this.objectStartPos.clear();
        this.objectStartPos.set(object.id, { x: object.x, y: object.y });
    }

    startMultiDrag(point: Point) {
        if (this.selectedObjects.length === 0) return;
        this.isDragging = true;
        this.dragStart = point;
        this.objectStartPos.clear();
        for (const obj of this.selectedObjects) {
            this.objectStartPos.set(obj.id, { x: obj.x, y: obj.y });
        }
    }

    updateDrag(point: Point) {
        if (!this.isDragging || !this.dragStart) return;

        const dx = point.x - this.dragStart.x;
        const dy = point.y - this.dragStart.y;

        for (const obj of this.selectedObjects) {
            const start = this.objectStartPos.get(obj.id);
            if (start) {
                obj.x = start.x + dx;
                obj.y = start.y + dy;
                obj.bounds.x = obj.x;
                obj.bounds.y = obj.y;
            }
        }
    }

    endDrag() {
        this.isDragging = false;
        this.dragStart = null;
        this.objectStartPos.clear();
    }
}
