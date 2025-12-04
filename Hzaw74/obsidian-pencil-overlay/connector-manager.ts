import { DrawableObject } from "./interaction-manager";

export interface Connector {
    id: string;
    sourceId: string;
    targetId: string;
    path: string;
}

export class ConnectorManager {
    connectors: Connector[] = [];

    createConnector(source: DrawableObject, target: DrawableObject): Connector {
        const id = Date.now().toString() + "-conn";
        const connector: Connector = {
            id,
            sourceId: source.id,
            targetId: target.id,
            path: this.calculatePath(source, target)
        };
        this.connectors.push(connector);
        return connector;
    }

    updateConnectors(objects: DrawableObject[]) {
        const objMap = new Map(objects.map(o => [o.id, o]));

        for (const conn of this.connectors) {
            const source = objMap.get(conn.sourceId);
            const target = objMap.get(conn.targetId);

            if (source && target) {
                conn.path = this.calculatePath(source, target);
            }
        }
    }

    calculatePath(source: DrawableObject, target: DrawableObject): string {
        // Simple center-to-center line for now
        const startX = source.bounds.x + source.bounds.w / 2;
        const startY = source.bounds.y + source.bounds.h / 2;
        const endX = target.bounds.x + target.bounds.w / 2;
        const endY = target.bounds.y + target.bounds.h / 2;

        return `M ${startX} ${startY} L ${endX} ${endY}`;
    }
}
