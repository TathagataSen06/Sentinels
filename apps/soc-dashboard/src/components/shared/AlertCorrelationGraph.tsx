"use client";

import { memo, useMemo, useCallback } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  type Edge, 
  type Node, 
  Position, 
  MarkerType,
  Handle,
  type NodeProps
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Activity, ShieldAlert, KeyRound, Server, Globe, type LucideIcon } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

// --- Custom Node Definitions ---

interface CustomNodeData {
  label: string;
  detail: string;
  badge?: string;
  [key: string]: unknown;
}

interface StyledNodeProps {
  data: CustomNodeData;
  icon: LucideIcon;
  colorClass: string;
  bgClass: string;
  borderColorClass: string;
}

const CustomNode = memo(({ data, icon: Icon, colorClass, bgClass, borderColorClass }: StyledNodeProps) => (
  <div className={`flex flex-col items-center gap-3 w-40 text-center bg-gray-950 p-4 rounded-xl border-2 ${borderColorClass} shadow-xl relative transition-transform hover:scale-105`}>
    <Handle type="target" position={Position.Left} className="!w-2 !h-2 !bg-gray-500 !border-none" />
    <div className={`p-4 rounded-full border-2 ${borderColorClass} ${bgClass}`}>
      <Icon size={24} className={colorClass} />
    </div>
    <div>
      <p className="font-semibold text-sm text-gray-200">{data.label}</p>
      <p className="text-xs text-gray-500 font-mono mt-1">{data.detail}</p>
      {data.badge && (
        <Badge variant="outline" className="mt-2 text-[10px] bg-black/40">
          {data.badge}
        </Badge>
      )}
    </div>
    <Handle type="source" position={Position.Right} className="!w-2 !h-2 !bg-gray-500 !border-none" />
  </div>
));
CustomNode.displayName = 'CustomNode';

const ThreatActorNode = memo(({ data }: NodeProps) => <CustomNode data={data as unknown as CustomNodeData} icon={Globe} colorClass="text-red-500" bgClass="bg-red-500/10" borderColorClass="border-red-900/50" />);
ThreatActorNode.displayName = 'ThreatActorNode';

const ReconNode = memo(({ data }: NodeProps) => <CustomNode data={data as unknown as CustomNodeData} icon={Activity} colorClass="text-orange-500" bgClass="bg-orange-500/10" borderColorClass="border-orange-900/50" />);
ReconNode.displayName = 'ReconNode';

const CredentialNode = memo(({ data }: NodeProps) => <CustomNode data={data as unknown as CustomNodeData} icon={KeyRound} colorClass="text-yellow-500" bgClass="bg-yellow-500/10" borderColorClass="border-yellow-900/50" />);
CredentialNode.displayName = 'CredentialNode';

const CommandNode = memo(({ data }: NodeProps) => <CustomNode data={data as unknown as CustomNodeData} icon={Server} colorClass="text-red-500" bgClass="bg-red-500/10" borderColorClass="border-red-900/50" />);
CommandNode.displayName = 'CommandNode';

const IncidentNode = memo(({ data }: NodeProps) => <CustomNode data={data as unknown as CustomNodeData} icon={ShieldAlert} colorClass="text-blue-500" bgClass="bg-blue-500/10" borderColorClass="border-blue-900/50" />);
IncidentNode.displayName = 'IncidentNode';

// CRITICAL: nodeTypes MUST be defined outside the component to prevent infinite re-renders
const nodeTypes = {
  threatActor: ThreatActorNode,
  recon: ReconNode,
  credential: CredentialNode,
  command: CommandNode,
  incident: IncidentNode,
};

// --- Mock Graph Data (static) ---

const initialNodes: Node[] = [
  { id: '1', type: 'threatActor', position: { x: 50, y: 150 }, data: { label: 'Attacker IP', detail: '192.168.1.105', badge: 'Tor Exit Node' } },
  { id: '2', type: 'recon', position: { x: 300, y: 150 }, data: { label: 'Reconnaissance', detail: 'HTTP Port Scan', badge: 'T1595' } },
  { id: '3', type: 'credential', position: { x: 550, y: 50 }, data: { label: 'Credential Access', detail: 'SSH Brute Force', badge: 'T1110' } },
  { id: '4', type: 'credential', position: { x: 550, y: 250 }, data: { label: 'Credential Access', detail: 'Web Login Bypass', badge: 'T1190' } },
  { id: '5', type: 'command', position: { x: 800, y: 150 }, data: { label: 'Command Execution', detail: 'wget rootkit.sh', badge: 'T1059' } },
  { id: '6', type: 'incident', position: { x: 1050, y: 150 }, data: { label: 'Incident Triggered', detail: 'INC-2041', badge: 'CRITICAL' } },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' } },
  { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
  { id: 'e2-4', source: '2', target: '4', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
  { id: 'e3-5', source: '3', target: '5', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' } },
  { id: 'e4-5', source: '4', target: '5', animated: true, style: { stroke: '#ef4444', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' } },
  { id: 'e5-6', source: '5', target: '6', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
];

export function AlertCorrelationGraph() {
  return (
    <div className="w-full h-[400px] border border-gray-800 rounded-xl overflow-hidden bg-gray-950/50">
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        nodeTypes={nodeTypes}
        fitView
        className="bg-transparent"
        minZoom={0.5}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#374151" gap={24} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
