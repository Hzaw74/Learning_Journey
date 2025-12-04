import { EditorView, ViewPlugin, ViewUpdate } from "@codemirror/view";
import { InkEngine, Point } from "./ink-engine";
import { InteractionManager, DrawableObject } from "./interaction-manager";
import { ShapeRecognizer } from "./shape-recognizer";
import { ConnectorManager, Connector } from "./connector-manager";
import { OCRService } from "./ocr-service";
import { Toolbar, ToolType, ActionType } from "./toolbar";
import { Notice } from "obsidian";

export class CanvasLayer {
    canvas: HTMLCanvasElement;
    ctx: CanvasRenderingContext2D;
    view: EditorView;
    currentStroke: Point[] = [];
    isDrawing = false;
    objects: DrawableObject[] = [];

    // History
    history: DrawableObject[][] = [];
    historyIndex: number = -1;

    interactionManager: InteractionManager;
    connectorManager: ConnectorManager;
    toolbar: Toolbar;

    mode: 'draw' | 'select' | 'lasso' | 'pan' | 'erase' = 'draw';
    activeColor: string = '#000000';
    activeSize: number = 4;

    // Shape Snapping
    holdTimer: number | null = null;
    snappedShape: { type: string, path: string, bounds: any } | null = null;

    // Lasso
    lassoPolygon: Point[] = [];

    // Infinite Canvas
    transform = { x: 0, y: 0, scale: 1 };
    isPanning = false;
    panStart = { x: 0, y: 0 };

    constructor(view: EditorView) {
        this.view = view;
        this.interactionManager = new InteractionManager();
        this.connectorManager = new ConnectorManager();

        this.canvas = document.createElement("canvas");
        this.canvas.className = "pencil-overlay-canvas";
        this.canvas.style.position = "absolute";
        this.canvas.style.top = "0";
        this.canvas.style.left = "0";
        this.canvas.style.pointerEvents = "auto";
        this.canvas.style.zIndex = "100";
        this.canvas.style.background = "transparent";
        this.canvas.style.transformOrigin = "0 0";
        this.canvas.style.touchAction = "none"; // Prevent iPad Scribble

        this.view.contentDOM.parentElement?.appendChild(this.canvas);

        this.ctx = this.canvas.getContext("2d")!;

        // Toolbar
        this.toolbar = new Toolbar(this.view.contentDOM.parentElement!,
            (tool: ToolType, color: string, size: number) => {
                this.activeColor = color;
                this.activeSize = size;

                if (tool === 'eraser') {
                    this.mode = 'erase';
                    this.canvas.style.cursor = 'crosshair';
                } else if (tool === 'select') {
                    this.mode = 'select'; // Default to select, right-click to lasso
                    this.canvas.style.cursor = 'default';
                } else if (tool === 'pan') {
                    this.mode = 'pan';
                    this.canvas.style.cursor = 'grab';
                } else {
                    this.mode = 'draw';
                    this.canvas.style.cursor = 'default';
                }
            },
            (action: ActionType) => {
                if (action === 'undo') this.undo();
                else if (action === 'redo') this.redo();
                else if (action === 'clear') this.clear();
            }
        );

        this.saveHistory(); // Initial state
        this.resize();
        this.setupEventListeners();
    }

    saveHistory() {
        // Remove future history if we are in the middle
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }
        // Deep copy objects
        const snapshot = JSON.parse(JSON.stringify(this.objects));
        this.history.push(snapshot);
        this.historyIndex++;

        // Limit history size
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.objects = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
            this.render();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.objects = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
            this.render();
        }
    }

    clear() {
        if (confirm("Clear all drawings?")) {
            this.objects = [];
            this.saveHistory();
            this.render();
        }
    }

    resize() {
        const rect = this.view.contentDOM.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.render();
    }

    setupEventListeners() {
        this.canvas.addEventListener("pointerdown", this.onPointerDown.bind(this));
        this.canvas.addEventListener("pointermove", this.onPointerMove.bind(this));
        this.canvas.addEventListener("pointerup", this.onPointerUp.bind(this));
        this.canvas.addEventListener("wheel", this.onWheel.bind(this), { passive: false });

        this.canvas.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            // Cycle modes (excluding erase, which is set by toolbar)
            if (this.mode === 'draw') this.mode = 'select';
            else if (this.mode === 'select') this.mode = 'lasso';
            else if (this.mode === 'lasso') this.mode = 'pan';
            else this.mode = 'draw';

            new Notice(`Switched to mode: ${this.mode}`);
            this.render();
        });

        // Keyboard shortcuts
        window.addEventListener("keydown", this.onKeyDown.bind(this));
        window.addEventListener("keyup", this.onKeyUp.bind(this));
    }

    async onKeyDown(e: KeyboardEvent) {
        if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            if (e.shiftKey) this.redo();
            else this.undo();
        }

        if (e.key === 't' || e.key === 'T') {
            if (this.interactionManager.selectedObjects.length > 0) {
                new Notice("Recognizing text...");
                const strokes = this.interactionManager.selectedObjects
                    .filter(o => o.type === 'stroke' && o.points)
                    .map(o => ({ points: o.points! }));

                try {
                    const text = await OCRService.recognizeStrokes(strokes);
                    new Notice(`Recognized: ${text}`);
                    console.log("OCR Result:", text);
                    navigator.clipboard.writeText(text);
                } catch (err) {
                    console.error(err);
                    new Notice("OCR Failed");
                }
            }
        }
        if (e.code === 'Space') {
            if (this.mode !== 'pan') {
                this.canvas.style.cursor = 'grab';
            }
        }
    }

    onKeyUp(e: KeyboardEvent) {
        if (e.code === 'Space') {
            this.canvas.style.cursor = 'default';
        }
    }

    onWheel(e: WheelEvent) {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const zoomSensitivity = 0.001;
            const delta = -e.deltaY * zoomSensitivity;
            const newScale = Math.min(Math.max(0.1, this.transform.scale + delta), 5);

            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const wx = (x - this.transform.x) / this.transform.scale;
            const wy = (y - this.transform.y) / this.transform.scale;

            this.transform.scale = newScale;
            this.transform.x = x - wx * newScale;
            this.transform.y = y - wy * newScale;

            this.render();
        }
    }

    getPoint(e: PointerEvent): Point {
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.clientX - rect.left;
        const clientY = e.clientY - rect.top;

        return {
            x: (clientX - this.transform.x) / this.transform.scale,
            y: (clientY - this.transform.y) / this.transform.scale,
            p: e.pressure
        };
    }

    onPointerDown(e: PointerEvent) {
        if (this.mode === 'pan' || e.buttons === 4 || (e.buttons === 1 && e.getModifierState("Space"))) {
            this.isPanning = true;
            this.panStart = { x: e.clientX, y: e.clientY };
            this.canvas.setPointerCapture(e.pointerId);
            this.canvas.style.cursor = 'grabbing';
            return;
        }

        const point = this.getPoint(e);

        if (this.mode === 'erase') {
            this.isDrawing = true;
            this.currentStroke = [point]; // Eraser trail
            this.canvas.setPointerCapture(e.pointerId);
            this.eraseAt(point);
            return;
        }

        if (this.mode === 'select') {
            const hit = this.interactionManager.hitTest(this.objects, point);
            if (hit) {
                if (this.interactionManager.selectedObjects.includes(hit)) {
                    this.interactionManager.startMultiDrag(point);
                } else {
                    this.interactionManager.startDrag(hit, point);
                }
                this.canvas.setPointerCapture(e.pointerId);
                this.render();
            } else {
                this.interactionManager.selectedObjects = [];
                this.interactionManager.selectedObject = null;
                this.render();
            }
            return;
        }

        if (this.mode === 'lasso') {
            this.isDrawing = true;
            this.lassoPolygon = [point];
            this.canvas.setPointerCapture(e.pointerId);
            return;
        }

        if (e.pointerType !== "pen" && e.pointerType !== "mouse") return;
        this.isDrawing = true;
        this.currentStroke = [point];
        this.snappedShape = null;
        this.canvas.setPointerCapture(e.pointerId);

        this.resetHoldTimer();
    }

    onPointerMove(e: PointerEvent) {
        if (this.isPanning) {
            const dx = e.clientX - this.panStart.x;
            const dy = e.clientY - this.panStart.y;
            this.transform.x += dx;
            this.transform.y += dy;
            this.panStart = { x: e.clientX, y: e.clientY };
            this.render();
            return;
        }

        const point = this.getPoint(e);

        if (this.mode === 'erase') {
            if (!this.isDrawing) return;
            this.eraseAt(point);
            this.render();
            return;
        }

        if (this.mode === 'select') {
            if (this.interactionManager.isDragging) {
                this.interactionManager.updateDrag(point);
                this.connectorManager.updateConnectors(this.objects);
                this.render();
            }
            return;
        }

        if (this.mode === 'lasso') {
            if (!this.isDrawing) return;
            this.lassoPolygon.push(point);
            this.render();
            return;
        }

        if (!this.isDrawing) return;

        if (this.snappedShape) return;

        this.currentStroke.push(point);
        this.render();

        this.resetHoldTimer();
    }

    eraseAt(point: Point) {
        const eraserRadius = 10;
        let erased = false;
        for (let i = this.objects.length - 1; i >= 0; i--) {
            const obj = this.objects[i];
            if (point.x >= obj.bounds.x - eraserRadius && point.x <= obj.bounds.x + obj.bounds.w + eraserRadius &&
                point.y >= obj.bounds.y - eraserRadius && point.y <= obj.bounds.y + obj.bounds.h + eraserRadius) {
                // Remove object
                this.objects.splice(i, 1);
                erased = true;
            }
        }
        if (erased) {
            // We don't save history on every frame of erase, maybe just on up?
            // For now, let's save on up.
        }
    }

    resetHoldTimer() {
        if (this.holdTimer) window.clearTimeout(this.holdTimer);
        this.holdTimer = window.setTimeout(() => {
            if (this.isDrawing && this.currentStroke.length > 10) {
                this.trySnapShape();
            }
        }, 600);
    }

    trySnapShape() {
        const shape = ShapeRecognizer.recognize(this.currentStroke);
        if (shape) {
            console.log("Snapped to:", shape.type);
            if (shape.path) {
                this.snappedShape = { type: shape.type, path: shape.path, bounds: shape.bounds };
                this.render();
            }
        }
    }

    onPointerUp(e: PointerEvent) {
        if (this.isPanning) {
            this.isPanning = false;
            this.canvas.releasePointerCapture(e.pointerId);
            this.canvas.style.cursor = this.mode === 'pan' ? 'grab' : 'default';
            return;
        }

        if (this.mode === 'erase') {
            this.isDrawing = false;
            this.canvas.releasePointerCapture(e.pointerId);
            this.saveHistory(); // Save after erase
            this.render();
            return;
        }

        if (this.holdTimer) window.clearTimeout(this.holdTimer);

        if (this.mode === 'select') {
            if (this.interactionManager.isDragging) {
                this.saveHistory(); // Save after move
            }
            this.interactionManager.endDrag();
            this.canvas.releasePointerCapture(e.pointerId);
            return;
        }

        if (this.mode === 'lasso') {
            this.isDrawing = false;
            this.canvas.releasePointerCapture(e.pointerId);

            this.interactionManager.selectInPolygon(this.objects, this.lassoPolygon);

            if (this.interactionManager.selectedObjects.length > 0) {
                this.mode = 'select';
                new Notice(`Selected ${this.interactionManager.selectedObjects.length} objects`);
            }

            this.lassoPolygon = [];
            this.render();
            return;
        }

        if (!this.isDrawing) return;
        this.isDrawing = false;
        this.canvas.releasePointerCapture(e.pointerId);

        if (this.currentStroke.length > 5) {
            const startPoint = this.currentStroke[0];
            const endPoint = this.currentStroke[this.currentStroke.length - 1];

            const startObj = this.interactionManager.hitTest(this.objects, startPoint);
            const endObj = this.interactionManager.hitTest(this.objects, endPoint);

            if (startObj && endObj && startObj !== endObj) {
                console.log("Creating connector!");
                this.connectorManager.createConnector(startObj, endObj);
                this.currentStroke = [];
                this.snappedShape = null;
                this.saveHistory(); // Save connector
                this.render();
                return;
            }
        }

        let path: string;
        let bounds: any;

        if (this.snappedShape) {
            path = this.snappedShape.path!;
            bounds = this.snappedShape.bounds;
        } else {
            path = InkEngine.getStrokePath(this.currentStroke, { size: this.activeSize });
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            for (const p of this.currentStroke) {
                minX = Math.min(minX, p.x);
                minY = Math.min(minY, p.y);
                maxX = Math.max(maxX, p.x);
                maxY = Math.max(maxY, p.y);
            }
            bounds = { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
        }

        this.objects.push({
            id: Date.now().toString(),
            type: 'stroke',
            path,
            points: [...this.currentStroke],
            x: bounds.x,
            y: bounds.y,
            bounds: bounds,
            color: this.activeColor
        });

        this.currentStroke = [];
        this.snappedShape = null;
        this.saveHistory(); // Save new stroke
        this.render();
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.save();
        this.ctx.translate(this.transform.x, this.transform.y);
        this.ctx.scale(this.transform.scale, this.transform.scale);

        this.ctx.strokeStyle = "#555";
        this.ctx.lineWidth = 2 / this.transform.scale;
        for (const conn of this.connectorManager.connectors) {
            const p = new Path2D(conn.path);
            this.ctx.stroke(p);
        }

        for (const obj of this.objects) {
            this.ctx.save();
            if (obj.path) {
                const p = new Path2D(obj.path);

                if (this.interactionManager.selectedObjects.includes(obj)) {
                    this.ctx.strokeStyle = "#00a8ff";
                    this.ctx.lineWidth = 1 / this.transform.scale;
                    this.ctx.strokeRect(obj.bounds.x - 5, obj.bounds.y - 5, obj.bounds.w + 10, obj.bounds.h + 10);
                }

                this.ctx.fillStyle = (obj as any).color || "black";
                this.ctx.fill(p);
            }
            this.ctx.restore();
        }

        if (this.lassoPolygon.length > 0) {
            this.ctx.beginPath();
            this.ctx.moveTo(this.lassoPolygon[0].x, this.lassoPolygon[0].y);
            for (let i = 1; i < this.lassoPolygon.length; i++) {
                this.ctx.lineTo(this.lassoPolygon[i].x, this.lassoPolygon[i].y);
            }
            this.ctx.closePath();
            this.ctx.strokeStyle = "#00a8ff";
            this.ctx.lineWidth = 1 / this.transform.scale;
            this.ctx.setLineDash([5 / this.transform.scale, 5 / this.transform.scale]);
            this.ctx.stroke();
            this.ctx.fillStyle = "rgba(0, 168, 255, 0.1)";
            this.ctx.fill();
            this.ctx.setLineDash([]);
        }

        if (this.snappedShape) {
            const p = new Path2D(this.snappedShape.path);
            this.ctx.strokeStyle = this.activeColor;
            this.ctx.lineWidth = 2 / this.transform.scale;
            this.ctx.stroke(p);
        } else if (this.currentStroke.length > 0) {
            const pathStr = InkEngine.getStrokePath(this.currentStroke, { size: this.activeSize });
            const p = new Path2D(pathStr);
            this.ctx.fillStyle = this.activeColor;
            this.ctx.fill(p);
        }

        this.ctx.restore();

        // UI Overlay
        this.ctx.font = "12px sans-serif";
        this.ctx.fillStyle = "gray";
        this.ctx.fillText(`Mode: ${this.mode} | Zoom: ${(this.transform.scale * 100).toFixed(0)}%`, 10, 20);
    }

    destroy() {
        this.canvas.remove();
        this.toolbar.destroy();
        window.removeEventListener("keydown", this.onKeyDown.bind(this));
        window.removeEventListener("keyup", this.onKeyUp.bind(this));
    }
}

export const pencilOverlayPlugin = ViewPlugin.fromClass(
    class {
        layer: CanvasLayer;

        constructor(view: EditorView) {
            this.layer = new CanvasLayer(view);
        }

        update(update: ViewUpdate) {
            if (update.docChanged || update.viewportChanged || update.geometryChanged) {
                this.layer.resize();
            }
        }

        destroy() {
            this.layer.destroy();
        }
    }
);
