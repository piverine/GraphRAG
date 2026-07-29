'use client';

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import with SSR disabled for react-force-graph-2d
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
});

interface GraphVisualizerProps {
  subgraph: any[];
}

export default function GraphVisualizer({ subgraph }: GraphVisualizerProps) {
  const graphData = useMemo(() => {
    const nodesMap = new Map<string, { id: string; label?: string; group?: string }>();
    const links: { source: string; target: string; label?: string }[] = [];

    if (!subgraph || !Array.isArray(subgraph)) {
      return { nodes: [], links: [] };
    }

    subgraph.forEach((step) => {
      // Handle tuple of records from CypherQAChain intermediate steps
      if (typeof step === 'object' && step !== null) {
        Object.entries(step).forEach(([key, val]) => {
          if (val && typeof val === 'object' && 'id' in val) {
            const id = String((val as any).id);
            if (!nodesMap.has(id)) {
              nodesMap.set(id, { id, label: id, group: key });
            }
          }
        });
      }
    });

    return {
      nodes: Array.from(nodesMap.values()),
      links,
    };
  }, [subgraph]);

  return (
    <div className="w-full h-full min-h-[400px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden relative flex flex-col justify-center items-center">
      {graphData.nodes.length === 0 ? (
        <div className="text-center p-6">
          <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-3 text-cyan-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p className="text-slate-400 text-sm font-medium">No Subgraph Rendered Yet</p>
          <p className="text-slate-600 text-xs mt-1">Ask a question or select a query to visualize retrieved facts.</p>
        </div>
      ) : (
        <div className="w-full h-full">
          <ForceGraph2D
            graphData={graphData}
            nodeAutoColorBy="group"
            nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
              const label = node.id;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Inter, sans-serif`;
              
              ctx.beginPath();
              ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
              ctx.fillStyle = node.color || '#38bdf8';
              ctx.fill();
              
              ctx.fillStyle = '#f8fafc';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(label, node.x, node.y + 10);
            }}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
          />
        </div>
      )}
    </div>
  );
}
