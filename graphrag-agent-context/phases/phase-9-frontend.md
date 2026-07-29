# Phase 9: Frontend Design (Next.js)

## Goal
Build the upload UI, chat UI, and — critically — the graph visualizer.

## Page Structure
- **Upload page** — drag-and-drop PDF, calls `/upload`, displays extraction summary.
- **Chat page** — message list + input, calls `/query`, renders the answer.
- **Graph visualizer** — renders the subgraph returned with each answer. **Not optional.**

## Why the Visualizer Is Not Optional
"Here's the answer" is a normal chatbot. "Here's the answer, and here's the exact chain of nodes/edges that produced it" is the entire verifiability thesis of the project made visible. This is the single highest-impact addition for making the project demo-able.

```jsx
import { ForceGraph2D } from 'react-force-graph';

function GraphVisualizer({ subgraph }) {
  const data = {
    nodes: subgraph.nodes.map(n => ({ id: n.id, label: n.type })),
    links: subgraph.relationships.map(r => ({
      source: r.start, target: r.end, label: r.type
    })),
  };
  return <ForceGraph2D graphData={data} nodeLabel="label" linkLabel="label" />;
}
```

## Visualization Library Options
| Library | Notes |
|---|---|
| react-force-graph | Simple force-directed layout, good default, minimal setup |
| vis-network | More configuration options, slightly heavier |
| Neo4j NVL (Neo4j Visualization Library) | Purpose-built for Neo4j data shapes; worth exploring for deeper native integration |

## Definition of Done
- [ ] Upload page successfully calls `/upload` and displays a real extraction summary
- [ ] Chat page successfully calls `/query` and displays the answer
- [ ] Graph visualizer renders the subgraph returned alongside each chat answer
- [ ] Visualizer remains readable (not an unreadable tangle) by limiting subgraph size returned per query to what's relevant to the question
