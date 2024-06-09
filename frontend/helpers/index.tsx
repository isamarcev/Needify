import { IOption } from '@/components/Selector/types';

export const getOptionsFromEnum = (e: Record<string, string>): IOption[] =>
  Object.values(e).map((item) => ({
    id: item,
    label: item,
  }));
