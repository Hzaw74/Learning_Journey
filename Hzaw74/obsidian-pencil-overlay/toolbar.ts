export type ToolType = 'pen' | 'marker' | 'eraser' | 'select' | 'pan';
export type ActionType = 'undo' | 'redo' | 'clear';

export class Toolbar {
    element: HTMLElement;
    activeTool: ToolType = 'pen';
    activeColor: string = '#000000';
    activeSize: number = 4;

    onToolChange: (tool: ToolType, color: string, size: number) => void;
    onAction: (action: ActionType) => void;

    constructor(container: HTMLElement,
        onToolChange: (tool: ToolType, color: string, size: number) => void,
        onAction: (action: ActionType) => void) {
        this.onToolChange = onToolChange;
        this.onAction = onAction;
        this.element = document.createElement('div');
        this.element.className = 'pencil-overlay-toolbar';
        this.element.style.position = 'absolute';
        this.element.style.bottom = '30px'; // Higher up
        this.element.style.left = '50%';
        this.element.style.transform = 'translateX(-50%)';
        this.element.style.display = 'flex';
        this.element.style.gap = '16px'; // More gap
        this.element.style.padding = '16px'; // More padding
        this.element.style.background = 'white';
        this.element.style.borderRadius = '24px'; // Rounder
        this.element.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2)';
        this.element.style.zIndex = '200';
        this.element.style.alignItems = 'center';

        container.appendChild(this.element);
        this.render();
    }

    render() {
        this.element.innerHTML = '';

        // Tools Group
        const tools: { type: ToolType, label: string, icon: string }[] = [
            { type: 'pen', label: 'Pen', icon: '✏️' },
            { type: 'marker', label: 'Marker', icon: '🖍️' },
            { type: 'eraser', label: 'Eraser', icon: '🧹' },
            { type: 'select', label: 'Select/Lasso', icon: '✋' },
            { type: 'pan', label: 'Pan', icon: '✥' }
        ];

        const toolGroup = document.createElement('div');
        toolGroup.style.display = 'flex';
        toolGroup.style.gap = '8px';

        tools.forEach(tool => {
            const btn = this.createButton(tool.icon, tool.label, this.activeTool === tool.type, () => {
                this.activeTool = tool.type;
                if (tool.type === 'marker') {
                    this.activeSize = 10;
                    this.activeColor = 'rgba(255, 255, 0, 0.5)';
                } else if (tool.type === 'pen') {
                    this.activeSize = 4;
                    this.activeColor = '#000000';
                }
                this.update();
            });
            toolGroup.appendChild(btn);
        });
        this.element.appendChild(toolGroup);

        // Separator
        this.addSeparator();

        // Color Picker
        const colors = ['#000000', '#FF0000', '#0000FF', '#008000'];
        const colorContainer = document.createElement('div');
        colorContainer.style.display = 'flex';
        colorContainer.style.gap = '12px'; // Larger gap

        colors.forEach(color => {
            const btn = document.createElement('div');
            btn.style.width = '32px'; // Larger touch target
            btn.style.height = '32px';
            btn.style.borderRadius = '50%';
            btn.style.background = color;
            btn.style.cursor = 'pointer';
            btn.style.border = this.activeColor === color ? '3px solid #000' : '2px solid #ddd';

            btn.onclick = () => {
                this.activeColor = color;
                this.update();
            };

            colorContainer.appendChild(btn);
        });
        this.element.appendChild(colorContainer);

        // Separator
        this.addSeparator();

        // Size Slider
        const sliderContainer = document.createElement('div');
        sliderContainer.style.display = 'flex';
        sliderContainer.style.alignItems = 'center';
        sliderContainer.style.gap = '8px';

        const sliderLabel = document.createElement('span');
        sliderLabel.innerText = 'Size:';
        sliderLabel.style.fontSize = '14px';
        sliderLabel.style.fontWeight = 'bold';
        sliderContainer.appendChild(sliderLabel);

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '1';
        slider.max = '20';
        slider.value = this.activeSize.toString();
        slider.style.width = '100px'; // Wider slider
        slider.style.height = '20px'; // Taller touch area
        slider.oninput = (e) => {
            this.activeSize = parseInt((e.target as HTMLInputElement).value);
            this.onToolChange(this.activeTool, this.activeColor, this.activeSize);
        };
        sliderContainer.appendChild(slider);
        this.element.appendChild(sliderContainer);

        // Separator
        this.addSeparator();

        // Actions (Undo/Redo)
        const actions: { type: ActionType, label: string, icon: string }[] = [
            { type: 'undo', label: 'Undo', icon: '↩️' },
            { type: 'redo', label: 'Redo', icon: '↪️' },
            { type: 'clear', label: 'Clear All', icon: '🗑️' }
        ];

        const actionGroup = document.createElement('div');
        actionGroup.style.display = 'flex';
        actionGroup.style.gap = '8px';

        actions.forEach(action => {
            const btn = this.createButton(action.icon, action.label, false, () => {
                this.onAction(action.type);
            });
            actionGroup.appendChild(btn);
        });
        this.element.appendChild(actionGroup);
    }

    createButton(icon: string, title: string, active: boolean, onClick: () => void): HTMLButtonElement {
        const btn = document.createElement('button');
        btn.innerText = icon;
        btn.title = title;
        btn.style.padding = '12px 16px'; // Larger touch target
        btn.style.borderRadius = '12px';
        btn.style.border = 'none';
        btn.style.background = active ? '#e0e0e0' : 'transparent';
        btn.style.cursor = 'pointer';
        btn.style.fontSize = '24px'; // Larger icon
        btn.onclick = onClick;
        return btn;
    }

    addSeparator() {
        const sep = document.createElement('div');
        sep.style.width = '2px';
        sep.style.height = '32px';
        sep.style.background = '#eee';
        sep.style.margin = '0 8px';
        this.element.appendChild(sep);
    }

    update() {
        this.render();
        this.onToolChange(this.activeTool, this.activeColor, this.activeSize);
    }

    destroy() {
        this.element.remove();
    }
}
