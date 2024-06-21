import { create } from 'zustand';
import { IStore } from '@/store/types';

const useStore = create<IStore>()((set) => ({
  user: { telegram_id: 0 },
  setUser: (user) => set({ user }),
}));
