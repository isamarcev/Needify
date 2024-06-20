import { IOption } from '@/components/Selector/types';
import { ICategoryRaw, ICurrency, ITaskRaw } from '@/services/types';
import { ITaskShortCard } from '@/widgets/TaskCard/types';
import { format } from 'date-fns';

export const getOptionsFromEnum = (e: Record<string, string>): IOption[] =>
  Object.values(e).map((item) => ({
    id: item,
    label: item,
  }));

export const categoriesRawToOptions = (
  categoriesRaw: ICategoryRaw[],
): IOption[] => categoriesRaw.map(({ title }) => ({ id: title, label: title }));

export const tasksRawToShortCards = (tasksRaw: ITaskRaw[]): ITaskShortCard[] =>
  tasksRaw.map(({ task_id, title, deadline, price }) => {
    return {
      id: task_id,
      title,
      deadline: format(deadline, 'PP'),
      price,
    };
  });

export const currenciesRawToOptions = (currenciesRaw: ICurrency[]): IOption[] =>
  currenciesRaw.map(({ symbol }) => ({ id: symbol, label: symbol }));
