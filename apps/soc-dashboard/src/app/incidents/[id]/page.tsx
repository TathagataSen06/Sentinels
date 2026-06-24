"use client";

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Activity, ShieldAlert, KeyRound, Server, type LucideIcon } from 'lucide-react';
import { AlertCorrelationGraph, type CorrelationStage } from '@/components/shared/AlertCorrelationGraph';
import { useIncident, useUpdateIncident } from '@/lib/hooks/useIncident';
import type { IncidentEvent } from '@/lib/api';

// Map a MITRE tactic to a node type + timeline icon.
function stageTypeForTactic(tactic: string): CorrelationStage['type'] {
  const t = tactic.toLowerCase();
  if (t.includes('recon')) return 'recon';
  if (t.includes('execution') || t.includes('lateral')) return 'command';
  return 'credential';
}

const TACTIC_ICON: Record<CorrelationStage['type'], LucideIcon> = {
  recon: Activity,
  credential: KeyRound,
  command: Server,
};

// Collapse the event stream into ordered, de-duplicated kill-chain stages.
function deriveStages(events: IncidentEvent[]): CorrelationStage[] {
  const seen = new Set<string>();
  const stages: CorrelationStage[] = [];
  for (const e of events) {
    const key = e.tactic || e.event_type;
    if (seen.has(key)) continue;
    seen.add(key);
    stages.push({
      type: stageTypeForTactic(e.tactic || ''),
      label: e.tactic || 'Activity',
      detail: e.event_type || e.plugin,
      technique: e.technique_id && e.technique_id !== 'Unknown' ? e.technique_id : undefined,
    });
  }
  return stages;
}

const SEVERITY_BADGE: Record<string, string> = {
  CRITICAL: 'bg-red-600',
  HIGH: 'bg-orange-600',
  MEDIUM: 'bg-yellow-600',
  LOW: 'bg-blue-600',
};

export default function IncidentInvestigation() {
  const params = useParams();
  const id = (params?.id as string) || '';

  const { data: incident, isLoading, error } = useIncident(id);
  const updateIncident = useUpdateIncident(id);
  const [activeTab, setActiveTab] = useState('overview');

  const stages = useMemo(() => deriveStages(incident?.events ?? []), [incident?.events]);

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500">Loading incident…</div>;
  }
  if (error || !incident) {
    return (
      <div className="p-8 text-center text-red-500">
        Failed to load incident.{' '}
        <Link href="/incidents" className="underline">Back to incidents</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in duration-500">
      <header className="flex flex-col gap-4">
        <Link href="/incidents" className="text-sm text-gray-400 hover:text-white flex items-center gap-2 w-fit transition-colors">
          <ArrowLeft size={16} /> Back to Incidents
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-3xl font-bold flex items-center gap-3">
                {incident.title}
              </h2>
              <Badge variant="destructive" className={`text-sm ${SEVERITY_BADGE[incident.severity] ?? 'bg-gray-600'}`}>
                {incident.severity}
              </Badge>
              <Badge variant="outline" className="text-sm bg-orange-500/20 text-orange-400 border-orange-500/50">
                {incident.status}
              </Badge>
            </div>
            <p className="text-gray-400 mt-2">
              Source <span className="font-mono text-red-400">{incident.source_ip}</span>
              {incident.sensor_name && <> · sensor <span className="font-mono">{incident.sensor_name}</span></>}
              {' · '}{incident.event_count} event{incident.event_count === 1 ? '' : 's'}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/20"
              disabled={updateIncident.isPending}
              onClick={() => updateIncident.mutate({ status: 'CONTAINED' })}
            >
              Contain
            </Button>
            <Button
              variant="default"
              className="bg-blue-600 hover:bg-blue-700"
              disabled={updateIncident.isPending}
              onClick={() => updateIncident.mutate({ status: 'INVESTIGATING', assignee: 'You' })}
            >
              Assign to Me
            </Button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1">

        {/* Main Content Area (2 columns) */}
        <div className="xl:col-span-2 space-y-6 flex flex-col">

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle>Attack Chain Correlation</CardTitle>
            </CardHeader>
            <CardContent className="p-0 border-none">
              <AlertCorrelationGraph
                sourceIp={incident.source_ip}
                incidentLabel={incident.id.slice(0, 8)}
                severity={incident.severity}
                stages={stages}
              />
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800 flex-1">
            <CardHeader className="border-b border-gray-800 pb-0">
              <div className="flex gap-6">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`pb-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview' ? 'border-blue-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'}`}
                >
                  Event Logs
                </button>
                <button
                  onClick={() => setActiveTab('notes')}
                  className={`pb-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'notes' ? 'border-blue-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'}`}
                >
                  Analyst Notes
                </button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {activeTab === 'overview' ? (
                <div className="space-y-4 font-mono text-xs text-gray-300">
                  {incident.events.length === 0 ? (
                    <p className="text-gray-500">No events recorded for this incident yet.</p>
                  ) : (
                    incident.events.map((e, i) => (
                      <div key={i} className="p-4 bg-gray-950 rounded-md border border-gray-800 flex flex-col sm:flex-row gap-2 sm:gap-4">
                        <span className="text-gray-500 shrink-0">{format(new Date(e.time), 'HH:mm:ss')}</span>
                        <span className="text-blue-400 shrink-0">{e.plugin}:</span>
                        <span className="break-all">
                          {e.event_type}
                          {e.technique_id && e.technique_id !== 'Unknown' && (
                            <span className="text-gray-500"> ({e.technique_id})</span>
                          )}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <textarea
                    className="w-full h-32 bg-gray-950 border border-gray-800 rounded-md p-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none text-gray-200"
                    placeholder="Add investigation notes here..."
                  ></textarea>
                  <Button size="sm">Save Note</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Area (1 column) */}
        <div className="space-y-6 flex flex-col">

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle className="text-lg">Incident Timeline</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-6">
                {stages.length === 0 ? (
                  <p className="text-gray-500 text-sm">Awaiting correlated activity.</p>
                ) : (
                  stages.map((stage, i) => {
                    const Icon = TACTIC_ICON[stage.type] ?? ShieldAlert;
                    return (
                      <div key={i} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full border border-gray-800 bg-gray-950 shrink-0 shadow">
                            <Icon size={14} className="text-blue-400" />
                          </div>
                          {i < stages.length - 1 && <div className="w-px h-full bg-gray-800 my-1"></div>}
                        </div>
                        <div className="pb-6">
                          <div className="flex items-center gap-2 mb-1">
                            <div className="font-semibold text-sm text-gray-200">{stage.label}</div>
                            {stage.technique && (
                              <span className="font-mono text-xs text-gray-500 ml-auto">{stage.technique}</span>
                            )}
                          </div>
                          <div className="text-gray-400 text-xs">{stage.detail}</div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="border-b border-gray-800 pb-4">
              <CardTitle className="text-lg">Threat Intel</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Attacker IP</p>
                <div className="flex items-center justify-between p-3 bg-gray-950 rounded border border-gray-800">
                  <span className="font-mono text-red-400">{incident.source_ip}</span>
                  <Badge variant="outline" className="bg-red-500/20 text-red-400 border-red-500/50">
                    {incident.severity}
                  </Badge>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-800">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">MITRE ATT&CK</p>
                <div className="flex flex-wrap gap-2">
                  {incident.mitre.length === 0 ? (
                    <span className="text-sm text-gray-500">No techniques mapped yet.</span>
                  ) : (
                    incident.mitre.map((t) => (
                      <Badge key={t} variant="outline" className="font-mono bg-black/40">{t}</Badge>
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
