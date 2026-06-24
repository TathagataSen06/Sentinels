import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchIncident, updateIncident, type ApiIncidentDetail } from '../api';

export const useIncident = (id: string | undefined) =>
  useQuery({
    queryKey: ['incident', id],
    queryFn: () => fetchIncident(id as string),
    enabled: Boolean(id),
    refetchInterval: 10_000,
  });

export const useUpdateIncident = (id: string | undefined) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { status?: string; assignee?: string }) =>
      updateIncident(id as string, body),
    onSuccess: (updated: ApiIncidentDetail) => {
      queryClient.setQueryData(['incident', id], updated);
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    },
  });
};
