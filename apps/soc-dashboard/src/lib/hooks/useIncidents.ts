import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { useTenantStore } from '../store/useTenantStore';
import { fetchIncidents, type Severity } from '../api';

export interface Incident {
  id: string;
  title: string;
  severity: Severity;
  status: string;
  assignee: string | null;
  sensor: string;
  sourceIp: string;
  mitre: string[];
  time: string;
}

export const useIncidents = () => {
  const activeTenantId = useTenantStore((state) => state.activeTenantId);

  return useQuery({
    queryKey: ['incidents', activeTenantId],
    queryFn: async (): Promise<Incident[]> => {
      const page = await fetchIncidents();
      return page.items.map((i) => ({
        id: i.id,
        title: i.title,
        severity: i.severity,
        status: i.status,
        assignee: i.assignee,
        sensor: i.sensor_name || '—',
        sourceIp: i.source_ip,
        mitre: i.mitre,
        time: formatDistanceToNow(new Date(i.last_seen), { addSuffix: true }),
      }));
    },
    // Keep the SOC view fresh as the processing engine correlates new activity.
    refetchInterval: 10_000,
  });
};
