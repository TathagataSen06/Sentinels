import { useQuery } from '@tanstack/react-query';
import { useTenantStore } from '../store/useTenantStore';

export interface Incident {
  id: string;
  title: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'NEW' | 'INVESTIGATING' | 'CONTAINED' | 'RESOLVED' | 'CLOSED';
  assignee: string | null;
  sensor: string;
  time: string;
  mitre: string[];
}

const mockIncidents: Incident[] = [
  { id: 'INC-2041', title: 'SSH Brute Force Campaign', severity: 'CRITICAL', status: 'NEW', sensor: 'eu-west-1a-ssh', time: '2 mins ago', assignee: null, mitre: ['T1110.001'] },
  { id: 'INC-2040', title: 'Suspicious WGET Command', severity: 'HIGH', status: 'INVESTIGATING', sensor: 'us-east-web', time: '15 mins ago', assignee: 'T. Sen', mitre: ['T1059.004'] },
  { id: 'INC-2039', title: 'Failed Login Anomaly', severity: 'MEDIUM', status: 'CONTAINED', sensor: 'db-honeypot-01', time: '1 hour ago', assignee: 'J. Doe', mitre: ['T1078'] },
  { id: 'INC-2038', title: 'Port Scan Detected', severity: 'LOW', status: 'RESOLVED', sensor: 'edge-router-sim', time: '3 hours ago', assignee: 'Auto-Bot', mitre: ['T1046'] },
  { id: 'INC-2037', title: 'SMB Enumeration', severity: 'HIGH', status: 'NEW', sensor: 'corp-file-share', time: '4 hours ago', assignee: null, mitre: ['T1039'] },
];

export const useIncidents = () => {
  const activeTenantId = useTenantStore((state) => state.activeTenantId);

  return useQuery({
    queryKey: ['incidents', activeTenantId],
    queryFn: async () => {
      // Simulate network latency
      await new Promise(resolve => setTimeout(resolve, 600));
      return mockIncidents;
    },
  });
};
