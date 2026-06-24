"use client";

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { ShieldAlert, Users, Clock, Filter, SlidersHorizontal } from 'lucide-react';
import { useIncidents } from '@/lib/hooks/useIncidents';

export default function IncidentManagement() {
  const { data: incidents, isLoading, error } = useIncidents();

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <ShieldAlert className="text-blue-500" size={32} />
            Incident Management
          </h2>
          <p className="text-gray-400 mt-2">Triage, investigate, and remediate security incidents</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><SlidersHorizontal size={16}/> Views</Button>
          <Button variant="outline" className="gap-2"><Filter size={16}/> Filter</Button>
        </div>
      </header>

      <Card className="flex-1 bg-gray-900 border-gray-800 flex flex-col overflow-hidden">
        <CardHeader className="border-b border-gray-800 bg-gray-950 flex flex-row items-center justify-between pb-4">
          <CardTitle>All Incidents</CardTitle>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">Showing {incidents?.length || 0} incidents</span>
          </div>
        </CardHeader>
        <CardContent className="p-0 flex-1 overflow-auto">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">Loading incidents...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">Failed to load incidents.</div>
          ) : !incidents || incidents.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <ShieldAlert className="mx-auto mb-3 text-gray-700" size={40} />
              <p className="font-medium text-gray-400">No incidents yet</p>
              <p className="text-sm mt-1">Incidents appear here as sensors report attacker activity and the engine correlates it.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Incident ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>Sensor</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidents?.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="font-mono text-xs text-gray-400">{inc.id}</TableCell>
                    <TableCell className="font-medium">{inc.title}</TableCell>
                    <TableCell>
                      <Badge variant={
                        inc.severity === 'CRITICAL' ? 'destructive' :
                        inc.severity === 'HIGH' ? 'warning' :
                        inc.severity === 'MEDIUM' ? 'default' : 'secondary'
                      }>
                        {inc.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs uppercase tracking-wider font-semibold text-gray-400">
                        {inc.status}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Users size={14} className="text-gray-500" />
                        <span className="text-sm text-gray-300">{inc.assignee || 'Unassigned'}</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-gray-400">{inc.sensor}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 text-gray-400">
                        <Clock size={14} />
                        <span className="text-sm">{inc.time}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link 
                        href={`/incidents/${inc.id}`} 
                        className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background hover:bg-gray-800 hover:text-gray-100 h-9 px-4 py-2 border border-gray-700 bg-transparent text-gray-200"
                      >
                        Investigate
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
