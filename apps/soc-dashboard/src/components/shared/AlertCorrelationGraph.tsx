"use client";

import { memo, useMemo } from 'react';
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

// --- Stage typing ------------------------------------------------------------

export interface CorrelationStage {
  type: 'recon' | 'credential' | 'command';
  label: string;
  detail: string;
  technique?: string;
}

export interface AlertCorrelationGraphProps {
  sourceIp?: string;
  incidentLabel?: string;
  severity?: string;
  stages?: CorrelationStage[];
}

const EDGE_COLORS: Record<string, string> = {
  recon: '#f59e0b',
  credential: '#eab308',
  command: '#ef4444',
  incident: '#3b82f6',
};

// Static demo chain — used only when the component is rendered without props.
const demoStages: CorrelationStage[] = [
  { type: 'recon', label: 'Reconnaissance', detail: 'HTTP Port Scan', technique: 'T1595' },
  { type: 'credential', label: 'Credential Access', detail: 'SSH Brute Force', technique: 'T1110' },
  { type: 'command', label: 'Command Execution', detail: 'wget rootkit.sh', technique: 'T1059' },
];

function buildGraph(
  sourceIp: string,
  incidentLabel: string,
  severity: string,
  stages: CorrelationStage[],
): { nodes: Node[]; edges: Edge[] } {
  const colX = (i: number) => 50 + i * 240;
  const nodes: Node[] = [
    {
      id: 'attacker',
      type: 'threatActor',
      position: { x: colX(0), y: 150 },
      data: { label: 'Attacker IP', detail: sourceIp },
    },
  ];
  const edges: Edge[] = [];
  let prevId = 'attacker';

  stages.forEach((stage, idx) => {
    const id = `stage-${idx}`;
    nodes.push({
      id,
      type: stage.type,
      position: { x: colX(idx + 1), y: 150 },
      data: { label: stage.label, detail: stage.detail, badge: stage.technique },
    });
    const color = EDGE_COLORS[stage.type] ?? '#6b7280';
    edges.push({
      id: `e-${prevId}-${id}`, source: prevId, target: id, animated: true,
      style: { stroke: color, strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color },
    });
    prevId = id;
  });

  nodes.push({
    id: 'incident',
    type: 'incident',
    position: { x: colX(stages.length + 1), y: 150 },
    data: { label: 'Incident', detail: incidentLabel, badge: severity },
  });
  edges.push({
    id: `e-${prevId}-incident`, source: prevId, target: 'incident', animated: true,
    style: { stroke: EDGE_COLORS.incident, strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: EDGE_COLORS.incident },
  });

  return { nodes, edges };
}

export function AlertCorrelationGraph({
  sourceIp = '192.168.1.105',
  incidentLabel = 'INC-2041',
  severity = 'CRITICAL',
  stages = demoStages,
}: AlertCorrelationGraphProps) {
  const { nodes, edges } = useMemo(
    () => buildGraph(sourceIp, incidentLabel, severity, stages.length ? stages : demoStages),
    [sourceIp, incidentLabel, severity, stages],
  );

  return (
    <div className="w-full h-[400px] border border-gray-800 rounded-xl overflow-hidden bg-gray-950/50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
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
