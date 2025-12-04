import { Plugin } from 'obsidian';
import { pencilOverlayPlugin } from './canvas-layer';

export default class PencilOverlayPlugin extends Plugin {
    async onload() {
        console.log('Loading Pencil Overlay Plugin');
        this.registerEditorExtension(pencilOverlayPlugin);
    }

    onunload() {
        console.log('Unloading Pencil Overlay Plugin');
    }
}
