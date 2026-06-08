import { create } from 'zustand';

interface TenantState {
  activeTenantId: string | null;
  setTenantId: (id: string) => void;
}

export const useTenantStore = create<TenantState>((set) => ({
  activeTenantId: 'tenant-01', // Default tenant
  setTenantId: (id) => set({ activeTenantId: id }),
}));
